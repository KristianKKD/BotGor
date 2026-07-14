from lib.MicroService import MicroServiceBase
from lib.Service_UI import Simple_UI

APP_NAME:str = "TWITCH"

class Twitch_Service(MicroServiceBase, Simple_UI):
    def __init__(self, ui_enabled:bool):

        MicroServiceBase.__init__(self=self, name=APP_NAME)
        if ui_enabled:
            Simple_UI.__init__(self=self, commands={})
        return