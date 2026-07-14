from collections import deque 
import asyncio

from dataclasses import dataclass

from lib.API_REST import post
from lib.API_Msgs import MSG

@dataclass
class Listener:
    name:str
    port:int

@dataclass
class Message:
    content:dict[str, str]
    url:str

class Broadcaster:
    def __init__(self, name=""):
        self.listeners:list[Listener] = []
        self.message_queue:deque[list[Message]] = deque([])
        self.processing:bool = False
        self.updating:bool = False
        self.name:str = name
        return

    def get_listeners(self) -> dict[str, str]:
        return {listener.name: str(listener.port) for listener in self.listeners}

    def broadcast(self, content:dict[str, str], url=MSG):
        msg:Message = Message(content=content, url=url)
        self.message_queue.append(msg)
        if not self.processing:
            asyncio.create_task(self.process_queue())
        return
    
    async def add_listener(self, name:str, port:int):
        if self.find_listener(name=name):
            print(f"{name} already in the listener list")
            return
        await self._lock_update_listeners(listener=Listener(name=name, port=port), add=True)
        return
    
    def remove_listener(self, name:str=None, port:int=None):
        listener:Listener = self.find_listener(name=name, port=port)
        if listener is not None:
            asyncio.create_task(self._lock_update_listeners(listener=listener, add=False))
        return

    async def process_queue(self):
        self.processing = True

        while(len(self.message_queue) > 0):
            while(self.updating):
                await asyncio.sleep(0.01)

            msg:Message = self.message_queue.popleft()
            json:dict[str, str] = msg.content

            for listener in self.listeners:
                print(f"{self.name} is broadcasting: {json} to {listener.name}")
                asyncio.create_task(post(msg=msg.url, port=listener.port, json=json, name=self.name))

        self.processing = False
        return
    
    def find_listener(self, name:str=None, port:int=None):
        if not name and not port:
            raise ValueError("Must pass name or port when finding listener!")
        
        # FIND BY PORT
        if not name: 
            for listener in self.listeners:
                if listener.port == port:
                    return listener
            return None
        
        # FIND BY NAME 
        for listener in self.listeners:
            if listener.name == name:
                return listener
        return None
    
    async def _lock_update_listeners(self, listener:Listener, add:bool):
        self.updating = True
        while(self.processing):
            await asyncio.sleep(0.01)

        if add:
            self.listeners.append(listener)
            print(f"{self.name} added {listener.name} to listeners!")
        else:
            self.listeners.remove(listener)
            print(f"{self.name} removed {listener.name} from listeners!")

        self.updating = False
        return
    