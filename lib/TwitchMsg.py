import json
from pydantic import BaseModel

class TwitchMsg(BaseModel):
    def __init__(self, user:str, content:str):
        self.user:str = user
        self.content:str = content
        return
    
    def to_json(self) -> str:
        return json.dumps(self)
    
    def __str__(self) -> str:
        return self.to_json()
