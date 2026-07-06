import os
import asyncio
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment
from Twitch.Twitch_Bot import Twitch_Bot
from Twitch.Twitch_API import Twitch_Service

FILTER_PATH:str = "censoredwords"

async def run_twitch():
    load_environment()

    service:Twitch_Service = Twitch_Service()
    twitch_bot:Twitch_Bot = Twitch_Bot(filtered_words=load_filtered_words(path=FILTER_PATH), broadcaster=service.broadcaster)
    await twitch_bot.login()
    while not service.shutdown:
        await asyncio.sleep(5)
    return

def load_filtered_words(path:str):
    slurs:list[str] = []
    if os.path.exists(path):
        with open(FILTER_PATH, "r") as f:
            slurs = [line.strip().lower() for line in f if line.strip()]
    return slurs

###############################################
if __name__ == "__main__":
    asyncio.run(run_twitch())