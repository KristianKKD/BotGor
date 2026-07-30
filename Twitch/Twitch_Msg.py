from dataclasses import dataclass
from lib.API_Msgs import NAME_KEY, CONTENT_KEY

@dataclass(slots=True)
class TwitchMsg:
    name:str
    content:str

    def to_json(self) -> dict[str, str]:
        return {NAME_KEY:self.name, CONTENT_KEY:self.content}

    def __str__(self) -> str:
        return str(self.to_json())
    