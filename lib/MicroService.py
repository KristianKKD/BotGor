import asyncio
from typing import Awaitable
from fastapi import FastAPI
from collections import defaultdict

from lib.Server import Server
from lib.Environment import find_port
from lib.Broadcaster import Broadcaster, Listener
from lib.API_REST import post

from lib.API_Msgs import DISCONNECT_MSG, JOIN_MSG, MSG_MSG, NAME_KEY, PORT_KEY, HEARTBEAT_MSG, RESPONSE_KEY

class MicroServiceBase(): # To be implemented as an API, then inherited as a parent
    def __init__(self, name:str, subscription_ports:list[int]=[], broadcaster:Broadcaster=None, commands:dict[str, Awaitable[bool]]=None):
        print(f"Starting {name}...")

        self.name:str = name
        self.shutdown:bool = False
        self.port:int = find_port(self.name)

        self.app:FastAPI = FastAPI(title=f"{name}:app")
        self.broadcaster:Broadcaster = broadcaster if broadcaster else Broadcaster(name=self.name)

        self.subscribed_broadcasters:dict[str, str] = {}

        self._subscription_ports:list[int] = subscription_ports
        self._register_api()
        server:Server = Server(app=self.app, port=self.port)
        asyncio.ensure_future(self.join_listeners(subscription_ports=subscription_ports))
        asyncio.ensure_future(self.start_heartbeats())
        return
    
    def __str__(self):
        return {NAME_KEY:{self.name}, PORT_KEY:{self.port}}

    def __del__(self):
        for listener in self.broadcaster.listeners:
            asyncio.run(post(msg=DISCONNECT_MSG, 
                            port=listener.port, 
                            body={NAME_KEY: self.name, PORT_KEY: self.port},
                            name=self.name
                            )
            )
        self.service_shutdown()
        return

    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        print(f"{self.name} received: {msg}")
        return {NAME_KEY: self.name, "received": "ok"}

    async def handle_inbound_join(self, req:dict[str, str]) -> dict[str, str]:
        print(f"Received join request: {req}")
        if not req:
            raise ValueError("Received empty join request!!")
        
        name:str = req.get(NAME_KEY, "")
        port:int = int(req.get(PORT_KEY, 0))
        if not name or not port:
            raise ValueError("Received empty name/port in join request!")
        
        await self.broadcaster.add_listener(name=name, port=port)
        listeners:dict[str, str] = {self.name : str(self.port)} | (self.broadcaster.get_listeners())
        print(f"{name} joined listeners, returning our listeners: {listeners}")
        return listeners
    
    async def handle_disconnect(self, msg:dict[str, str]) -> dict[str, str]:
        try:
            service_name:str = msg.get(NAME_KEY, "")
            service_port:int = int(msg.get(PORT_KEY, 0))
            print(f"{service_name}:{service_port} disconnected and is our subscription!")
        except ValueError:
            print(f"Invald disconnect msg: {msg}")
            pass

        print("Attempting to join the listeners again...")
        asyncio.create_task(self.join_listeners(subscription_ports=self._subscription_ports)) # Restart the join process if they are restarting
        return {NAME_KEY: self.name, PORT_KEY: self.port, DISCONNECT_MSG: "ok"}

    def service_shutdown(self):
        print(f"Shutting down {self.name}...")
        self.broadcaster.broadcast(url=DISCONNECT_MSG, content={NAME_KEY:self.name})
        self.shutdown = True
        return

    async def join_listeners(self, subscription_ports:list[int]) -> dict[str, str]:
        async def get_responses(subs:list[int]) -> dict[str, str]:
            responses:dict[str, str] = {}
            for port in subs:
                response:dict[str, str] = await post(msg=JOIN_MSG, 
                                                     port=port, 
                                                     body={NAME_KEY:self.name, PORT_KEY:str(self.port)},
                                                     name=self.name
                                                     )
                if response:
                    responses.update(response)
            return responses

        if len(subscription_ports) == 0:
            return {}

        print(f"{self.name} joining listeners...")

        to_join:list[int] = subscription_ports
        max_attempts:int = 1000
        
        for attempt in range(max_attempts):
            if attempt % 50 == 0 or attempt == 0:
                print(f"{self.name} joining listeners {subscription_ports} attempt:{attempt}/{max_attempts}")

            responses:dict[str, str] = await get_responses(subs=to_join)

            # Remove ports that responded successfully from the "to join" list
            new_listeners:dict[str, str] = {name:port for (name,port) in responses.items()
                                             if port not in self.subscribed_broadcasters.values() and port != str(self.port)}
            self.subscribed_broadcasters.update(new_listeners)
            to_join = [port for port in to_join if str(port) not in self.subscribed_broadcasters.values()]

            if not to_join:
                print(f"{self.name} joined all: {subscription_ports}")
                return self.subscribed_broadcasters
            
            await asyncio.sleep(1)

        print(f"{self.name} failed to join {subscription_ports}")
        return self.subscribed_broadcasters

    async def start_heartbeats(self):
        async def check_heartbeat(port:int) -> bool:
            response:dict[str, str] = await post(msg=HEARTBEAT_MSG, 
                                        port=port, 
                                        body={HEARTBEAT_MSG:self.name},
                                        name=self.name
                                        )
            return response.get(RESPONSE_KEY, None) == HEARTBEAT_MSG 

        TIMED_OUT_COUNT:int = 3

        failed_response:defaultdict[str, int] = defaultdict(list) # listener name, failed responses
        while not self.service_shutdown:
            to_remove:list[Listener] = []

            listener:Listener
            for listener in self.broadcaster.listeners:
                if not check_heartbeat(listener.port):
                    failed_response[listener.name] = failed_response[listener.name] + 1
                    if failed_response[listener.name] > TIMED_OUT_COUNT:
                        print(f"Failed to get a heartbeat from: {listener.name}")
                        to_remove.append(listener)
                        failed_response.pop(listener.name)

            listener:Listener
            for listener in to_remove:
                self.broadcaster.remove_listener(port=listener.port)

            asyncio.sleep(5)
        return

    def handle_heartbeat(self, msg:dict[str, str]) -> dict[str, str]:
        return {NAME_KEY:self.name, PORT_KEY:PORT_KEY, RESPONSE_KEY:HEARTBEAT_MSG}

    def _register_api(self):
        @self.app.post(f"/{JOIN_MSG}")
        async def join(req:dict[str, str]) -> dict[str, str]:
            try:
                return await self.handle_inbound_join(req=req)
            except:
                raise ValueError(f"{self.name} received an invalid {JOIN_MSG} msg! {req}")

        @self.app.post(f"/{MSG_MSG}")
        async def receive_msg(msg:dict[str, str]) -> dict[str, str]:
            try:
                return await self.handle_msg(msg=msg)
            except:
                raise ValueError(f"{self.name} received an invalid {MSG_MSG} msg! {msg}")
        
        @self.app.post(f"/{DISCONNECT_MSG}")
        async def disconnect(msg:dict[str, str]) -> dict[str, str]:
            try:
                return await self.handle_disconnect(msg=msg)
            except:
                raise ValueError(f"{self.name} received an invalid {DISCONNECT_MSG} msg! {msg}")

        @self.app.post(f"/{HEARTBEAT_MSG}")
        async def heartbeat(msg:dict[str, str]) -> dict[str, str]:
            try:
                return await self.handle_heartbeat(msg=msg)
            except:
                raise ValueError(f"{self.name} received an invalid {HEARTBEAT_MSG} msg! {msg}")