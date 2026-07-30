from typing import Any
from abc import ABC
from dataclasses import dataclass
from lib.API_Msgs import FONT_KEY, SIZE_KEY 

@dataclass(slots=True)
class Setting(ABC):
    def to_json(self) -> dict[str, Any]:
        return vars(self).items()
    
    def __str__(self) -> str:
        return str(self.to_json())

    @classmethod
    def from_json(cls, data:dict[str, Any]) -> 'Setting | None':
        """Try to construct this Setting from data. Return None if keys missing."""
        pass

@dataclass(slots=True)
class TwitchSettings(Setting):
    font:str = ""
    font_size:int = 0

    def to_json(self) -> dict[str, str]:
        return {
                FONT_KEY:self.font,
                SIZE_KEY:str(self.font_size)
                }

    @classmethod
    def from_json(cls, data:dict[str, Any]) -> 'TwitchSettings | None':
        return TwitchSettings(
            font=data.get(FONT_KEY, ""),
            font_size=int(data.get(SIZE_KEY, 0))
        )