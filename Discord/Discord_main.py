import time
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment, find_port
from lib.API_Comms import post, join_listeners

from Discord.Discord_Bot import Discord_Bot

#VOICE_CHANNEL_ID = 1416079575628251167 #DiscGor stream
#VOICE_CHANNEL_ID = 471406637643464724 #kami weebs
VOICE_CHANNEL_ID = 1201274493289648239 #kami chamber
#VOICE_CHANNEL_ID = 389460211666255882 #kami f

async def main():
    load_environment()

    bot:Discord_Bot = Discord_Bot(channel_id=VOICE_CHANNEL_ID)
    asyncio.create_task(bot.start(os.getenv("DISCORD_BOT_TOKEN")))

    while not bot.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(main())
    