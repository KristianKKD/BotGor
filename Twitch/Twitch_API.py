from lib.MicroService import MicroServiceBase

APP_NAME:str = "TWITCH"

class Twitch_Service(MicroServiceBase):
    def __init__(self):
        super().__init__(name=APP_NAME)
        return