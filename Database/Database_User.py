from dataclasses import dataclass
from lib.API_Msgs import NAME_KEY, FONT_KEY, SIZE_KEY, NAME_KEY, CONTENT_KEY

@dataclass(slots=True)
class UserMsg():
    name:str
    content:str
    font:str = ""
    font_size:int = 0

    def to_json(self) -> dict[str, str]:
        return {
                NAME_KEY:self.name, 
                CONTENT_KEY:self.content,
                FONT_KEY:self.font,
                SIZE_KEY:str(self.font_size)
                }

    def __str__(self) -> str:
        return str(self.to_json())

class User:
    def __init__(self, name:str="", font:str="", font_size:int=0, data:dict[str, str]=None):
        if data:
            self._load_data(data=data)
            return

        if not name:
            raise ValueError("Must provide name or data to user!")
        
        self.name:str = name
        self.font:str = font
        self.font_size:int = font_size
        return

    def _load_data(self, data:dict[str, str]):
        self.name = data.get(NAME_KEY, "")
        self.font:str = data.get(FONT_KEY, "")
        try:
            self.font_size:int = int(data.get(SIZE_KEY, 0))
        except:
            self.font_size:int = 0
        return

    def to_json(self) -> dict[str, str]:
        return {NAME_KEY:self.name, FONT_KEY:self.font, SIZE_KEY:str(self.font_size)}
    
    def __str__(self) -> str:
        return str(self.to_json())