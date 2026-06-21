from pydantic import BaseModel

from lib.MicroService import MicroServiceBase
from Twitch.Msg_Broadcaster import broadcaster

APP_NAME:str = "TWITCH"

class JoinRequest(BaseModel):
    port:int

class BotGorService(MicroServiceBase):
    def __init__(self):
        super().__init__(name=APP_NAME)
        
        @self.app.post("/join")
        async def join(req: JoinRequest) -> dict[str, str]:
            broadcaster.add_listener(req.port)
            return {str(index) : str(port) for index, port in enumerate(broadcaster.listener_ports)}