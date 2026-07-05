from lib.MicroService import MicroServiceBase
from lib.Environment import find_port
from lib.API_Comms import post

from Discord.Discord_Bot import Discord_Bot

APP_NAME:str = "DISCORD"

class Discord_Service(MicroServiceBase):
    def __init__(self, discord_bot:Discord_Bot):
        self._tts_port = find_port("TTS")
        self.discord_bot=discord_bot
        super().__init__(name=APP_NAME, subscription_ports=[self._tts_port])

    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        response:dict[str, str] = await super().handle_msg(msg)

        file_path:str = msg["path"]
        print(f"Playing msg:{file_path}")
        await self.discord_bot.queue_play(file_path=file_path)

        return response