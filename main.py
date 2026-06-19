from dotenv import load_dotenv
import asyncio
import os
import time

from Core.Twitch_Bot import KrabBot
from lib.Server import Server
from Core.BotGor_API import botgor

KEYS_PATH:str = "keys.env"
FILTER_PATH:str = "censoredwords"
PORTS_PATH:str = "ports.env"

async def launch_comms():
    print("Starting Server...")
    Server(app=botgor, port=os.environ["BOTGOR_PORT"])
    return

async def launch_botgor():
    print("Starting BotGor...")
    await KrabBot(filtered_words=load_filtered_words(path=FILTER_PATH)).connect()
    return

def load_filtered_words(path:str):
    slurs:list[str] = []
    if os.path.exists(path):
        with open("censoredwords", "r") as f:
            slurs = [line.strip().lower() for line in f if line.strip()]
    return slurs

###############################################
if __name__ == "__main__":
    load_dotenv(KEYS_PATH)
    if not os.environ["TWITCH_TOKEN"] or not os.environ["TWITCH_CLIENT_ID"]:
        raise ValueError("TWITCH_TOKEN and TWITCH_CLIENT_ID must be set in the environment variables.")
    
    load_dotenv(PORTS_PATH)
    if not os.environ["BOTGOR_PORT"]:
        raise ValueError("No BotGor port")
    
    asyncio.run(launch_comms())
    asyncio.run(launch_botgor())

    while True:
        time.sleep(1)
        print("beep")