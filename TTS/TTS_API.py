import json

from lib.Environment import find_port
from lib.MicroService import MicroServiceBase

APP_NAME:str = "TTS"

class TTS_Service(MicroServiceBase):
    def __init__(self):
        super().__init__(name=APP_NAME, subscription_ports=[find_port("TWITCH")])

        self.use_discord:bool = False

        @self.app.post("/use_discord")
        def use_discord(payload:dict[str, str]):
            try:
                data:dict[str, str] = json.loads(payload)
                use:bool = data["use_discord"]
                self.use_discord = use
            except:
                print(f"Data in payload was incorrectly parsed! Data: {payload}")
            return
        return
    
    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        response:dict[str, str] = await super().handle_msg(msg=msg)
        self.speak(text=msg["content"], user=msg["user"])
        return response
    
    async def handle_join(self, req:dict[str, str]) -> dict[str, str]:
        listeners:dict[str, str] = await super().handle_join(req)

        if not self.use_discord:
            discord_port:int = find_port("DISCORD")
            self.use_discord = discord_port in listeners.values()
        return listeners