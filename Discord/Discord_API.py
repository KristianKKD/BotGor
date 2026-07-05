from lib.MicroService import MicroServiceBase
from lib.Environment import find_port
from lib.API_Comms import post

APP_NAME:str = "DISCORD"

class Discord_Service(MicroServiceBase):
    def __init__(self):
        self._tts_port = find_port("TTS")
        super().__init__(name=APP_NAME, subscription_ports=self._tts_port)

        @self.app.post("/play")
        def receive_msg(msg:dict[str, str]) -> dict[str, str]:
            self.queue_play(file_path=msg["path"])
            return {"service": self.name, "status": "ok"}