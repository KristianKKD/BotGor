import time
import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment
from Discord.Discord_API import DiscordService

from Discord.DiscordBot import DiscordBot

async def main():
    load_environment()
    bot:DiscordBot = DiscordBot()
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))
    #discord_service:DiscordService = DiscordService(discord_bot=bot)

    # while discord_service and not discord_service.shutdown:
    #     time.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(main())
    