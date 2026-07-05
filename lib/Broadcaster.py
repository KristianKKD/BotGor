from collections import deque 
import asyncio

from dataclasses import dataclass

from lib.API_Comms import post

@dataclass
class Listener:
    name:str
    port:int

class Broadcaster:
    def __init__(self):
        self.listeners:list[Listener] = []
        self.message_queue:deque[dict[str, str]] = deque([])
        self.processing:bool = False
        self.updating:bool = False
        return

    def get_listeners(self) -> dict[str, str]:
        return {listener.name: str(listener.port) for listener in self.listeners}

    def broadcast(self, msg:dict[str, str]):
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
                asyncio.sleep(0.01)

            json:dict[str, str] = self.message_queue.popleft()
            print(f"Broadcasting: {json}")

            for listener in self.listeners:
                asyncio.create_task(post(msg="msg", port=listener.port, json=json))

        self.processing = False
        return
    
    def find_listener(self, name:str=None, port:int=None):
        if name is None and port is None:
            raise ValueError("Must pass name or port when finding listener!")
        
        if name is None:
            for listener in self.listeners:
                if listener.port == port:
                    return listener
            return None
        else: # PORT
            for listener in self.listeners:
                if listener.name == name:
                    return listener
            return None
    
    async def _lock_update_listeners(self, listener:Listener, add:bool):
        self.updating = True
        while(self.processing):
            asyncio.sleep(0.01)

        if add:
            self.listeners.append(listener)
        else:
            self.listeners.remove(listener)

        self.updating = False
        return
    