from fastapi import FastAPI

from lib.Server import Server
from lib.Environment import find_port
from lib.TwitchMsg import TwitchMsg

from abc import ABC, abstractmethod

class MicroServiceBase(ABC):
    name:str = ""
    shutdown:bool = False

    app = None

    def __init__(self, name:str):
        print(f"Starting {name}...")

        self.name:str = name
        self.shutdown = False
        self.port:int = find_port(self.name)

        self.app = FastAPI(title=f"{name}:app")
        server:Server = Server(app=self.app, port=find_port(name))

        @self.app.get("/health")
        def health() -> dict[str, str]:
            return {"service": self.name, "status": "ok"}

        @self.app.post("/shutdown")
        def close_server() -> dict[str, str]:
            self.shutdown = True
            return {"service": self.name, "status": "shutting_down"}
        
        @abstractmethod
        @self.app.post("/msg")
        def receive_msg(msg:TwitchMsg) -> dict[str, str]:
            return {"service": self.name, "received": "ok"}