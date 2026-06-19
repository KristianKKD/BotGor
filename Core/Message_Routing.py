from collections import deque 
import asyncio
import time

from Core.SimpleMsg import SimpleMsg
from lib.API_Comms import post

class Message_Router:
    def __init__(self):
        self.listener_ports:list[int] = []
        self.message_queue:deque[SimpleMsg] = deque([])
        self.processing:bool = False
        self.updating:bool = False
        return

    def incoming_message(self, msg:SimpleMsg):
        self.message_queue.append(msg)
        if not self.processing:
            asyncio.create_task(self.process_queue())
        return
    
    def add_listener(self, port:int):
        self.listener_ports.append(port)
        return
    
    def remove_listener(self, port:int):
        def lock_update_listeners():
            self.updating = True
            while(self.processing):
                time.sleep(0.01)

            self.listener_ports.remove(port)
            self.updating = False
            return
        
        asyncio.create_task(lock_update_listeners())
        return

    async def process_queue(self):
        self.processing = True

        while(len(self.message_queue) > 0):
            while(self.updating):
                time.sleep(0.01)

            msg:SimpleMsg = self.message_queue.popleft()
            json:str = msg.to_json()

            if msg.destination_port:
                post(content=json, port=msg.destination_port)
            else:
                for port in self.listener_ports:
                    post(content=json, port=port)

        self.processing = False
        return
    
router = Message_Router() # Singleton