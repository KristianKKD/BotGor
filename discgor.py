import asyncio

from TTS.TTS_main import run_tts
from Discord.Discord_main import run_discord
from Chatbot.Chatbot_main import run_ai

async def discgor():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_tts())
        tg.create_task(run_discord(channel_override=471406637643464724))
        tg.create_task(run_ai())

    return

if __name__ == "__main__":
    asyncio.run(discgor())