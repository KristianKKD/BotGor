import asyncio

from lib.MicroService import MicroServiceBase
from lib.Broadcaster import Broadcaster

from Socket.Socket_Comms import Socket_Comms

APP_NAME:str = "SOCKET"

class Socket_Service(MicroServiceBase):
    def __init__(self, comms:Socket_Comms, broadcaster:Broadcaster, ui_enabled:bool):
        self.comms:Socket_Comms = comms

        MicroServiceBase.__init__(self=self, name=APP_NAME, broadcaster=broadcaster, ui_enabled=ui_enabled)
        return

    
