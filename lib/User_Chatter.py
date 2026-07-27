from lib.API_Msgs import NAME_KEY, FONT_KEY, SIZE_KEY

class UserSettings:
    def __init__(self, name:str, font_name:str="", font_size:int=0):
        self.name:str = name
        self.font:str = font_name
        self.font_size:int = font_size
        return

    def to_json(self) -> dict[str, str]:
        return {NAME_KEY:self.name, FONT_KEY:self.font, SIZE_KEY:str(self.font_size)}

    def __str__(self) -> str:
        return str(self.to_json())