from lib.Environment import find_port
from lib.MicroService import MicroServiceBase
from lib.Broadcaster import Broadcaster

from TTS.TTS_Handler import TTS_Handler

APP_NAME:str = "TTS"

class TTS_Service(MicroServiceBase):
    def __init__(self, tts:TTS_Handler, broadcaster:Broadcaster):
        super().__init__(name=APP_NAME, subscription_ports=[find_port("TWITCH")], broadcaster=broadcaster)
        self.tts:TTS_Handler = tts
        return
    
    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        response:dict[str, str] = await super().handle_msg(msg=msg)

        user:str = msg.get("user", "")
        content:str = msg.get("content", "")
        if not user or not content:
            raise ValueError("Received empty user/content in msg!")
        
        await self.tts.speak(text=content, user=user)
        return response
    
    async def handle_inbound_join(self, req:dict[str, str]) -> dict[str, str]:
        listeners:dict[str, str] = await super().handle_inbound_join(req)

        if not self.tts.use_discord:
            discord_port:int = find_port("DISCORD")
            self.tts.use_discord = str(discord_port) == req.get("port", "")
        return listeners