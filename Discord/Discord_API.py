from lib.MicroService import MicroServiceBase
from Discord.DiscordBot import DiscordBot

APP_NAME:str = "DISCORD"

class DiscordService(MicroServiceBase):
    def __init__(self, discord_bot:DiscordBot):
        super().__init__(name=APP_NAME)
        
        @self.app.post("/play")
        def receive_msg(path:str) -> dict[str, str]:
            discord_bot.queue_play(file_path=path)
            return {"service": self.name, "status": "ok"}