from typing import Awaitable

from lib.Environment import find_port
from lib.MicroService import MicroServiceBase
from lib.Broadcaster import Broadcaster
from lib.Service_UI import Simple_UI
from lib.API_Msgs import PORT, OUTPUT_MSG
from lib.TwitchMsg import split_message

from TTS.TTS_Handler import TTS_Handler

APP_NAME:str = "TTS"

class TTS_Service(MicroServiceBase, Simple_UI):
    def __init__(self, tts:TTS_Handler, broadcaster:Broadcaster, ui_enabled:bool):
        self.tts:TTS_Handler = tts
        self.commands:dict[str, Awaitable] = {
            "tts": self.manual_tts,
            "stoptts": self.stop_tts,
            "voices": self.show_voices,
            "select": self.select_voice,
        }
    
        MicroServiceBase.__init__(self=self, name=APP_NAME, subscription_ports=[find_port("TWITCH"), find_port("CHATBOT"), find_port("GAMES")], broadcaster=broadcaster)
        if ui_enabled:
            Simple_UI.__init__(self=self, commands=self.commands)
        return
    
    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        response:dict[str, str] = MicroServiceBase.handle_msg(self=self, msg=msg)

        user:str
        content:str
        user, content = split_message(msg=msg)
        if not content: content = msg.get(OUTPUT_MSG, "")
        user = user or "Chatbot"

        if user and content:
            await self.tts.speak(text=content, user=user)
        
        return response
    
    async def handle_inbound_join(self, req:dict[str, str]) -> dict[str, str]:
        listeners:dict[str, str] = await MicroServiceBase.handle_inbound_join(self=self, req=req)

        if not self.tts.use_discord:
            discord_port:int = find_port("DISCORD")
            self.tts.use_discord = str(discord_port) == req.get(PORT, "")
        return listeners

    async def close_service(self, _) -> bool:
        await Simple_UI.close_service(self=self, _=_)
        await self.tts.stop_audio()
        return False

    async def stop_tts(self, _) -> bool:
        self.tts.stop_audio()
        return True

    async def manual_tts(self, content:str) -> bool:
        await self.tts.speak(text=content, user="UIGor")
        return True
    
    async def show_voices(self, _) -> bool:
        print(self.tts.engine.get_voices())
        return True

    async def select_voice(self, content:str) -> bool:
        self.tts.set_voice(voice=content)
        return True


       