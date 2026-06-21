import os
import time
import asyncio

from lib.Environment import load_environment
from Twitch.Twitch_Bot import KrabBot
from Twitch.BotGor_API import BotGorService

FILTER_PATH:str = "censoredwords"

async def main():
    load_environment()
    botgor_service:BotGorService = BotGorService()
    twitch_bot:KrabBot = KrabBot(filtered_words=load_filtered_words(path=FILTER_PATH))
    await twitch_bot.connect()

    while botgor_service and not botgor_service.shutdown:
        time.sleep(5)
    return

def load_filtered_words(path:str):
    slurs:list[str] = []
    if os.path.exists(path):
        with open("censoredwords", "r") as f:
            slurs = [line.strip().lower() for line in f if line.strip()]
    return slurs

###############################################
if __name__ == "__main__":
    asyncio.run(main())