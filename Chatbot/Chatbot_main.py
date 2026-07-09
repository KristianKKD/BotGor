import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment

from Chatbot.Chatbot_AIBot import AIBot
from Chatbot.Chatbot_API import Chatbot_Service

CONTEXT_ENABLED:bool = False
TRIGGER:str = "?"
MODEL_ID:str = "google/gemma-3-4b-it"
PROMPT_PREFIX:str = "A viewer says:"
PROMPT_SUFFIX:str = "Here is my reply:"

INITIAL_PROMPT:str = f"""
I am the friendly chatbot 'BotGor', I respond to 'viewer' messages with 50 words or less, incoming messages look like:
'{PROMPT_PREFIX}' username says message\n and then i will be prompted with '{PROMPT_PREFIX}'
which i will then respond to with 50 words or less in a a silly manner in general speech format.\n
I am grouchy and hate myself, making sure to make everyone else know that. I am generally awful to communicate with and mean spirited.
"""

async def handle_input(ai:AIBot):
    async def handle_exit(_):
        return False

    async def manual_msg(content):
        response:str = await ai.generate_response(prompt=content)
        print(response)
        return True
    
    commands = {
        "exit": handle_exit,
        "msg": manual_msg,
    }

    while True:
        user_input:str = str(await asyncio.to_thread(input, "Enter input:\n")).strip()
        cmd:str = user_input.lower().strip()
        arg:str = ""

        if ':' in user_input:
            cmd, arg = user_input.split(':', 1)

        if cmd in commands:
            if len(arg) > 0:
                should_continue = await commands[cmd](arg)
            else:
                should_continue = await commands[cmd]("")

            if not should_continue:
                break
        else:
            print("Invalid input:" + user_input)
    return

async def run_ai(manual_input:bool=False):
    load_environment()

    ai:AIBot = AIBot(model_id=MODEL_ID,
                     trigger=TRIGGER,
                     prefix=PROMPT_PREFIX,
                     suffix=PROMPT_SUFFIX,
                     initial_prompt=INITIAL_PROMPT,
                     enable_context=CONTEXT_ENABLED
                     )
    service:Chatbot_Service = Chatbot_Service(ai=ai)

    if manual_input:
        asyncio.create_task(handle_input(ai=ai))

    while not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_ai(manual_input=True))
    