from lib.MicroService import MicroServiceBase
from lib.Environment import find_port
from lib.API_Comms import post

APP_NAME:str = "DISCORD"

class Discord_Service(MicroServiceBase):
    def __init__(self):
        self._tts_port = find_port("TTS")
        super().__init__(name=APP_NAME, subscription_ports=self._tts_port)

        @self.app.post("/play")
        def receive_msg(path:str) -> dict[str, str]:
            self.queue_play(file_path=path)
            return {"service": self.name, "status": "ok"}
        
    async def handle_join(self, req:dict[str, str]) -> dict[str, str]:
        listeners:dict[str, str] = await super().handle_join(req)
        if self._tts_port in listeners:
            post("use_discord", self._tts_port, {"use_discord":str(True)})
        return