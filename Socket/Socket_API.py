from lib.MicroService import MicroServiceBase
from lib.Broadcaster import Broadcaster

from Socket.Socket_Comms import Socket_Comms

APP_NAME:str = "SOCKET"

class Socket_Service(MicroServiceBase):
    def __init__(self, broadcaster:Broadcaster, ui_enabled:bool):
        MicroServiceBase.__init__(self=self, name=APP_NAME, broadcaster=broadcaster, ui_enabled=ui_enabled)
        return