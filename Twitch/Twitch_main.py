import os
import asyncio
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment
from Twitch.Twitch_Bot import Twitch_Bot

FILTER_PATH:str = "censoredwords"

async def main():
    load_environment()

    twitch_bot:Twitch_Bot = Twitch_Bot(filtered_words=load_filtered_words(path=FILTER_PATH))
    await twitch_bot.start()
    while not twitch_bot.shutdown:
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
    asyncio.run(main())