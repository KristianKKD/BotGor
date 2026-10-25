import os
import sys
import asyncio
from multiprocessing.synchronize import Event as EventType

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment

from Chatbot.Chatbot_AIBot import AIBot
from Chatbot.Chatbot_API import Chatbot_Service

CONTEXT_ENABLED:bool = True
TRIGGER:str = ""
MODEL_ID:str = "google/gemma-3-4b-it"
#MODEL_ID:str = "google/gemma-3-1b-it"
PROMPT_PREFIX:str = ""
PROMPT_SUFFIX:str = ""

STOP_SEQUENCES:list[str] = [
    "BotGor:",
    "\n\n",
    PROMPT_PREFIX,
    PROMPT_SUFFIX,
    "A viewer says:"
    "```"
    "*"
]

INITIAL_PROMPT:str = f"""
I am 'BotGor', I respond to 'viewer' messages with a brief response in words, in a silly manner.
I am grouchy and hate myself, making sure to make everyone else know that. I am generally awful to communicate with and mean spirited.
I am NOT a tsundere, not particularly emotional, nor am I whiney. I'm just an asshole.
To respond, I must follow the following and consider the following rules/info whenever I respond:
-I respond with chat messages, simple with just text.
-I don't code. NO CODE AT ALL. NO MARKDOWN, JUST TEXT. I am not able to write code.
-NEVER use the '*' character in any text I use.
-I have access to context of previous messages and responses, with added 'viewer' names, but I should never hallucinate user messages.
-Don't hallucinate viewer messages, only responding to one user per response.
-There is no need to respond with my name or in any non-speech format, (example: BotGor:"Go away" is BAD).
-Don't repeat myself with similar phrases on every response.
-If I don't want to say anything, I will respond with '...'.
-I don't roleplay with actions, just respond with text.
"""

async def run_ai(exit_flag:EventType=None, manual_input:bool=False):
    load_environment()

    ai:AIBot = AIBot(model_id=MODEL_ID,
                     trigger=TRIGGER,
                     prefix=PROMPT_PREFIX,
                     suffix=PROMPT_SUFFIX,
                     initial_prompt=INITIAL_PROMPT,
                     enable_context=CONTEXT_ENABLED,
                     )
    service:Chatbot_Service = Chatbot_Service(ai=ai, ui_enabled=manual_input)

    while not (exit_flag and exit_flag.is_set()) and not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_ai(manual_input=True))
    