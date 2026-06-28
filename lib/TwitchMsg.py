import json

class TwitchMsg():
    def __init__(self, user:str, content:str):
        self.user:str = user
        self.content:str = content
        return

    def to_json(self) -> dict:
        return self.__dict__.copy()

    def __str__(self) -> str:
        return str(self.to_json())

if __name__ == "__main__":
    a = TwitchMsg(user="name", content="data")
    print(a)
    print(a.to_json())