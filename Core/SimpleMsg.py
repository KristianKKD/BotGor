import json

class SimpleMsg():
    def __init__(self, user:str, content:str, filtered_words:list[str]=[], destination_port:int=None):
        def has_slurs(message:str) -> bool:
            return any(word in message.lower() for word in filtered_words)
        
        self.user:str = user
        self.content:str = content if not has_slurs(content) else "filtered"
        self.destination_port:int = destination_port

        print(f"Message created: User: {user} Message: {content}")
        return
    
    def to_json(self) -> str:
        return json.dumps(self)
    
    def __str__(self) -> str:
        return self.to_json()
