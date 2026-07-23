import asyncio
from typing import Awaitable
from fastapi import FastAPI
from contextlib import asynccontextmanager

from lib.Server import Server
from lib.Environment import find_port
from lib.Broadcaster import Broadcaster
from lib.API_REST import post

from lib.API_Msgs import DISCONNECT, JOIN, MSG, NAME, PORT

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
        return
    
    def __str__(self):
        return {NAME:{self.name}, PORT:{self.port}}

    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        print(f"{self.name} received: {msg}")
        return {NAME: self.name, "received": "ok"}

    async def handle_inbound_join(self, req:dict[str, str]) -> dict[str, str]:
        print(f"Received join request: {req}")
        if not req:
            raise ValueError("Received empty join request!!")
        
        name:str = req.get(NAME, "")
        port:int = int(req.get(PORT, 0))
        if not name or not port:
            raise ValueError("Received empty name/port in join request!")
        
        await self.broadcaster.add_listener(name=name, port=port)
        listeners:dict[str, str] = {self.name : str(self.port)} | (self.broadcaster.get_listeners())
        print(f"{name} joined listeners, returning our listeners: {listeners}")
        return listeners
    
    async def handle_disconnect(self, msg:dict[str, str]) -> dict[str, str]:
        try:
            service_name:str = msg.get(NAME, "")
            service_port:int = int(msg.get(PORT, 0))
            print(f"{service_name}:{service_port} disconnected and is our subscription!")
        except ValueError:
            print(f"Invald disconnect msg: {msg}")
            pass

        print("Attempting to join the listeners again...")
        asyncio.create_task(self.join_listeners(subscription_ports=self._subscription_ports)) # Restart the join process if they are restarting
        return {NAME: self.name, PORT: self.port, DISCONNECT: "ok"}

    def service_shutdown(self):
        print(f"Shutting down {self.name}...")
        self.broadcaster.broadcast(content={NAME:self.name})
        self.shutdown = True
        return

    async def join_listeners(self, subscription_ports:list[int]) -> dict[str, str]:
        async def get_responses(subs:list[int]) -> dict[str, str]:
            responses:dict[str, str] = {}
            for port in subs:
                response:dict[str, str] = await post(msg=JOIN, 
                                                     port=port, 
                                                     json={NAME:self.name, PORT:str(self.port)},
                                                     name=self.name
                                                     )
                if response:
                    responses.update(response)
            return responses

        if len(subscription_ports) == 0:
            return {}

        print(f"{self.name} joining listeners...")

        to_join:list[int] = subscription_ports
        max_attempts:int = 100
        
        for attempt in range(max_attempts):
            if attempt % 20 == 0:
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

    def _register_api(self):
        # @asynccontextmanager
        # async def lifespan(app:FastAPI):
        #     await self.join_listeners(self._subscription_ports)
        
        @self.app.post(f"/{JOIN}")
        async def join(req:dict[str, str]) -> dict[str, str]:
            return await self.handle_inbound_join(req=req)

        @self.app.post(f"/{MSG}")
        async def receive_msg(msg:dict[str, str]) -> dict[str, str]:
            return await self.handle_msg(msg=msg)
        
        @self.app.post(f"/{DISCONNECT}")
        async def disconnect(msg:dict[str, str]) -> dict[str, str]:
            return await self.handle_disconnect(msg=msg)
        return