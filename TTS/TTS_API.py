from lib.MicroService import MicroServiceBase
from lib.TwitchMsg import TwitchMsg
from TTS.TTS_Base import TextToSpeechBase

APP_NAME:str = "TTS"

class TTSService(MicroServiceBase):
    def __init__(self, tts_engine:TextToSpeechBase):
        super().__init__(name=APP_NAME)
        
        self.discord_enabled=False

        @self.app.post("/msg")
        def receive_msg(msg:TwitchMsg) -> dict[str, str]:
            tts_engine.speak(text=msg.content, use_discord=self.discord_enabled)
            return {"service": self.name, "status": "ok"}