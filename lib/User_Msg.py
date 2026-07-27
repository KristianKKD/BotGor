from lib.API_Msgs import USER_KEY, CONTENT_KEY, FONT_KEY, SIZE_KEY

class UserMsg():
    def __init__(self, user:str, content:str, font:str="", font_size:int=0):
        self.user:str = user
        self.content:str = content
        self.font:str = font
        self.font_size:int = font_size
        return

    def to_json(self) -> dict:
        return {USER_KEY:self.user, CONTENT_KEY:self.content, FONT_KEY:self.font, SIZE_KEY:str(self.font_size)}

    def __str__(self) -> str:
        return str(self.to_json())


def split_message(msg:dict[str, str], key:str=USER_KEY, value:str=CONTENT_KEY) -> tuple[str, str]:
    name:str = msg.get(key, "") if key else ""
    content:str = msg.get(value, "") if value else "" 

    return name, content