from lib.MicroService import MicroServiceBase
from lib.TwitchMsg import TwitchMsg
from TTS.TTS_Handler import TTS_Handler
import json

APP_NAME:str = "TTS"

class TTSService(MicroServiceBase):
    def __init__(self, tts_handler:TTS_Handler):
        super().__init__(name=APP_NAME)

        @self.app.post("/use_discord")
        def use_discord(payload:str):
            try:
                use:bool = json.loads(payload)
                tts_handler.toggle_discord(use_discord=use)
            except:
                print(f"Data in payload was incorrectly parsed! Data: {payload}")
            return

        @self.app.post("/msg")
        def receive_msg(msg:TwitchMsg) -> dict[str, str]:
            tts_handler.speak(text=msg.content, user=msg.user)
            return {"service": self.name, "status": "ok"}