from lib.MicroService import MicroServiceBase
from lib.Environment import find_port
from lib.Service_UI import Simple_UI

from IO.IO_Handler import IO_Handler
from lib.API_Msgs import NAME_KEY, CONTENT_KEY

APP_NAME:str = "IO"

class IO_Service(MicroServiceBase, Simple_UI):
    def __init__(self, io_handler:IO_Handler, ui_enabled:bool):
        self.io_bot:IO_Handler = io_handler

        twitch_port:int = find_port("TWITCH")
        MicroServiceBase.__init__(self=self, name=APP_NAME, subscription_ports=[twitch_port])
        if ui_enabled:
            Simple_UI.__init__(self=self)
        return
    
    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        response:str = await MicroServiceBase.handle_msg(self=self, msg=msg)

        user:str = msg.get(NAME_KEY, "")
        content:str = msg.get(CONTENT_KEY, "")
        if user and content:
            self.io_bot.process_twitch_input(content=content)
            
        return response