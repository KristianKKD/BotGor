from lib.MicroService import MicroServiceBase
from lib.Environment import find_port

from Chatbot.Chatbot_AIBot import AIBot

APP_NAME:str = "CHATBOT"

class Chatbot_Service(MicroServiceBase):
    def __init__(self, ai:AIBot):
        self.ai:AIBot = ai

        twitch_port:int = find_port("TWITCH")
        super().__init__(name=APP_NAME, subscription_ports=[twitch_port])
        return
    
    async def handle_msg(self, msg:dict[str, str]):
        response:str = await super().handle_msg(msg=msg)
        if self.ai.busy:
            return {'response': 'Error: Model is busy, please try again.'}

        user:str = msg.get("user", "")
        content:str = msg.get("content", "")
        if not user or not content:
            raise ValueError("Received empty user/content in msg!")
        
        if content.startswith(self.ai.trigger):
            prompt:str = self.ai.create_prompt(user=user, content=content)
            context:list[str] = msg.get('context', [])
            
            output:str = await self.ai.generate_response(prompt=prompt, context=context)
            self.broadcaster.broadcast({'prompt':prompt, 'ai_output':output})

        return response
        
