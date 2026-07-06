import asyncio

from Twitch.Twitch_main import run_twitch
from TTS.TTS_main import run_tts
from Discord.Discord_main import run_discord

async def run_botgor():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_twitch())
        tg.create_task(run_tts())
        tg.create_task(run_discord())

    return

if __name__ == "__main__":
    asyncio.run(run_botgor())