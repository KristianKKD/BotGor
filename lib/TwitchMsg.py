from pydantic import BaseModel


class TwitchMsg(BaseModel):
    user: str
    content: str

    def to_json(self) -> str:
        return self.model_dump_json()

    def __str__(self) -> str:
        return self.to_json()
