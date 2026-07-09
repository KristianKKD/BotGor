import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from lib.Server import Server
from lib.Environment import find_port
from lib.Broadcaster import Broadcaster
from lib.API_Comms import post

class MicroServiceBase(): # To be implemented as an API, then inherited as a parent
    name:str = ""
    shutdown:bool = False

    app:FastAPI = None

    def __init__(self, name:str, subscription_ports:list[int]=[], broadcaster:Broadcaster=None):
        print(f"Starting {name}...")

        self.name:str = name
        self.shutdown:bool = False
        self.port:int = find_port(self.name)

        self.app:FastAPI = FastAPI(title=f"{name}:app")
        self.broadcaster:Broadcaster = broadcaster if broadcaster else Broadcaster()
        server:Server = Server(app=self.app, port=find_port(name))

        self._subscription_ports:list[int] = subscription_ports
        self._register_api()
        asyncio.ensure_future(self.join_listeners(subscription_ports=subscription_ports))
        return
    
    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        print(f"{self.name} received: {msg}")
        return {"service": self.name, "received": "ok"}

    async def handle_inbound_join(self, req:dict[str, str]) -> dict[str, str]:
        print(f"Received join request: {req}")
        if not req:
            raise ValueError("Received empty join request!!")
        
        name:str = req.get("name", "")
        port:int = int(req.get("port", 0))
        if not name or not port:
            raise ValueError("Received empty name/port in join request!")
        
        await self.broadcaster.add_listener(name=name, port=port)
        listeners:dict[str, str] = {self.name:str(self.port)} | (self.broadcaster.get_listeners())
        print(f"{name} joined listeners, returning our listeners: {listeners}")
        return listeners
    
    async def join_listeners(self, subscription_ports:list[int]) -> dict[str, str]:
        async def get_responses(subs:list[int]) -> dict[str, str]:
            responses:dict[str, str] = {}
            for port in subs:
                join_msg:str = "join"
                response:dict[str, str] = await post(msg=f"{join_msg}", port=port, json={"name":self.name, "port":str(self.port)})
                if response:
                    responses.update(response)
            return responses

        if len(subscription_ports) == 0:
            return {}

        print(f"{self.name} joining listeners...")

        to_join:list[int] = subscription_ports
        max_attempts:int = 100
        subscribed:dict[str, str] = {}
        for attempt in range(max_attempts):
            if attempt % 10 == 0:
                print(f"{self.name} joining listeners {subscription_ports} attempt:{attempt}/{max_attempts}")

            responses:dict[str, str] = await get_responses(subs=to_join)

            # Remove ports that responded successfully
            new_listeners:dict[str, str] = {name:port for (name,port) in responses.items() if port not in subscribed.values() and port != str(self.port)}
            subscribed.update(new_listeners)
            to_join = [port for port in to_join if str(port) not in subscribed.values()]

            if not to_join:
                print(f"{self.name} joined all: {subscription_ports}")
                return subscribed
            
            await asyncio.sleep(1)

        print(f"{self.name} failed to join {subscription_ports}")
        return {}

    def _register_api(self):
        @asynccontextmanager
        async def lifespan(app:FastAPI):
            await self.join_listeners(self._subscription_ports)

        @self.app.post("/shutdown")
        def close_server() -> dict[str, str]:
            self.shutdown = True
            return {"service": self.name, "status": "shutting_down"}
        
        @self.app.post("/join")
        async def join(req:dict[str, str]) -> dict[str, str]:
            return await self.handle_inbound_join(req=req)

        @self.app.post("/msg")
        async def receive_msg(msg:dict[str, str]) -> dict[str, str]:
            return await self.handle_msg(msg=msg)
        return