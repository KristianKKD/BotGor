import asyncio

from lib.MicroService import MicroServiceBase
from lib.Environment import find_port
from lib.Service_UI import Simple_UI
from lib.API_Msgs import CONTEXT_MSG, PROMPT_MSG, OUTPUT_MSG
from lib.TwitchMsg import split_message

from Chatbot.Chatbot_AIBot import AIBot

APP_NAME:str = "CHATBOT"

class Chatbot_Service(MicroServiceBase, Simple_UI):
    def __init__(self, ai:AIBot, ui_enabled:bool):
        self.ai:AIBot = ai

        MicroServiceBase.__init__(self=self, name=APP_NAME, subscription_ports=[find_port("DISCORD")])

        commands = {"msg": self.manual_msg}

        if ui_enabled:
            Simple_UI.__init__(self=self, commands=commands)
        return
    
    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        async def broadcast_response(prompt:str, context:list[str]):
            output:str = await self.ai.generate_response(prompt=prompt, context=context)
            self.broadcaster.broadcast({PROMPT_MSG:prompt, OUTPUT_MSG:output})
            return

        response:str = await MicroServiceBase.handle_msg(self=self, msg=msg)
        if self.ai.busy:
            return {OUTPUT_MSG: 'Error: Model is busy, please try again.'}

        user:str
        content:str
        user, content = split_message(msg=msg)
        if not content: content = msg.get(OUTPUT_MSG, "")
        if user and content:
            if not self.ai.trigger or content.startswith(self.ai.trigger):
                prompt:str = self.ai.create_prompt(user=user, content=content)
                context:list[str] = msg.get(CONTEXT_MSG, [])
                asyncio.create_task(broadcast_response(prompt=prompt, context=context))
        
        return response
        
    async def close_service(self, _) -> bool: # Automatically added into the pool of UI commands by default
        await Simple_UI.close_service(self=self, _=_)
        self.ai.__del__()
        return False

    async def manual_msg(self, content:str) -> bool:
        response:str = await self.ai.generate_response(prompt=content)
        self.broadcaster.broadcast({PROMPT_MSG:content, OUTPUT_MSG:response})
        print(response)
        return True