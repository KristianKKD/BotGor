from lib.API_Msgs import USER, CONTENT

class TwitchMsg():
    def __init__(self, user:str, content:str):
        self.user:str = user
        self.content:str = content
        return

    def to_json(self) -> dict:
        return {USER:self.user, CONTENT:self.content}

    def __str__(self) -> str:
        return str(self.to_json())


def split_message(msg:dict[str, str], key:str=USER, value:str=CONTENT) -> tuple[str, str]:
    name:str = msg.get(key, "") if key else ""
    content:str = msg.get(value, "") if value else "" 

    return name, content