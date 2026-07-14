import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment

from Discord.Discord_Bot import Discord_Bot
from Discord.Discord_API import Discord_Service

from lib.Broadcaster import Broadcaster

from STT.STT_Handler import STT_Handler
from STT.STT_Whisper import WhisperTranscriber

VOICE_CHANNEL_ID = 1416079575628251167 #DiscGor stream
#VOICE_CHANNEL_ID = 471406637643464724 #kami weebs
#VOICE_CHANNEL_ID = 1201274493289648239 #kami chamber
#VOICE_CHANNEL_ID = 389460211666255882 #kami f

async def run_discord(manual_input:bool=False, channel_override:int=None):
    load_environment()

    channel:int = channel_override if channel_override else VOICE_CHANNEL_ID

    broadcaster:Broadcaster = Broadcaster(name="DISCORD")
    stt:STT_Handler = STT_Handler(model=WhisperTranscriber())
    bot:Discord_Bot = Discord_Bot(channel_id=channel, broadcaster=broadcaster, stt=stt)
    service:Discord_Service = Discord_Service(discord_bot=bot, broadcaster=broadcaster, ui_enabled=manual_input)
    asyncio.create_task(bot.start(os.getenv("DISCORD_BOT_TOKEN")))

    while not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_discord(manual_input=True, channel_override=471406637643464724))
    