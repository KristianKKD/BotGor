from collections import deque 
import asyncio
import time

from lib.TwitchMsg import TwitchMsg
from lib.API_Comms import post

class Msg_Broadcaster:
    def __init__(self):
        self.listener_ports:list[int] = []
        self.message_queue:deque[TwitchMsg] = deque([])
        self.processing:bool = False
        self.updating:bool = False
        return

    def __str__(self) -> str:
        
        return

    async def incoming_message(self, msg:TwitchMsg):
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

            msg:TwitchMsg = self.message_queue.popleft()
            json:str = msg.to_json()

            for port in self.listener_ports:
                post(msg="msg", data=json, port=port)

        self.processing = False
        return
    
broadcaster = Msg_Broadcaster() # Singleton