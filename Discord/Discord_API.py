import os

from lib.MicroService import MicroServiceBase
from lib.Service_UI import Simple_UI
from lib.Environment import find_port

from Discord.Discord_Bot import Discord_Bot
from lib.API_Msgs import PATH_MSG, STOP_MSG
from lib.Broadcaster import Broadcaster

APP_NAME:str = "DISCORD"

class Discord_Service(MicroServiceBase, Simple_UI):
    def __init__(self, discord_bot:Discord_Bot, broadcaster:Broadcaster, ui_enabled:bool):
        self._tts_port:int = find_port("TTS")
        self.discord_bot:Discord_Bot = discord_bot
        MicroServiceBase.__init__(self=self, name=APP_NAME, subscription_ports=[self._tts_port], broadcaster=broadcaster)
        
        if ui_enabled:
            Simple_UI.__init__(self=self)
        return

    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        response:dict[str, str] = await MicroServiceBase.handle_msg(self=self, msg=msg)

        file_path:str = msg.get(PATH_MSG, "")
        if file_path and os.path.exists(file_path):
            print(f"Playing msg:{file_path}")
            await self.discord_bot.queue_play(file_path=file_path)
        elif file_path:
            print(f"No audio file generated at: {file_path}")
        
        return response
    
    def _register_api(self):
        MicroServiceBase._register_api(self=self)

        @self.app.post(f"/{STOP_MSG}")
        async def stop_audio(req:dict[str, str]) -> dict[str, str]:
            self.discord_bot.stop_audio()
            return
        return