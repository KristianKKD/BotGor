import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment

from Chatbot.Chatbot_AIBot import AIBot
from Chatbot.Chatbot_API import Chatbot_Service

CONTEXT_ENABLED:bool = False
TRIGGER:str = ""
MODEL_ID:str = "google/gemma-3-4b-it"
PROMPT_PREFIX:str = "A viewer says:"
PROMPT_SUFFIX:str = "Here is my reply:"

INITIAL_PROMPT:str = f"""
I am 'BotGor', I respond to 'viewer' messages with 50 words or less.
I will respond to messages with 50 words or less in a a silly manner in general speech format.
I shouldn't hallucinate viewer messages as they will be given to me one at a time.
I am grouchy and hate myself, making sure to make everyone else know that. I am generally awful to communicate with and mean spirited.
"""

async def run_ai(manual_input:bool=False):
    load_environment()

    ai:AIBot = AIBot(model_id=MODEL_ID,
                     trigger=TRIGGER,
                     prefix=PROMPT_PREFIX,
                     suffix=PROMPT_SUFFIX,
                     initial_prompt=INITIAL_PROMPT,
                     enable_context=CONTEXT_ENABLED
                     )
    service:Chatbot_Service = Chatbot_Service(ai=ai, ui_enabled=manual_input)

    while not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_ai(manual_input=True))
    