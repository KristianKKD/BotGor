from lib.MicroService import MicroServiceBase

APP_NAME:str = "TWITCH"

class Twitch_Service(MicroServiceBase):
    def __init__(self, ui_enabled:bool):

        MicroServiceBase.__init__(self=self, name=APP_NAME, ui_enabled=ui_enabled)
        return