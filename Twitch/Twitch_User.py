class TwitchUserSettings:
    def __init__(self, name:str, font_name:str="", font_size:int=0):
        self.name:str = name
        self.font:str = font_name
        self.font_size:int = font_size
        return