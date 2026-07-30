import asyncio
from typing import Awaitable

from Twitch.Twitch_main import run_twitch
from TTS.TTS_main import run_tts
from Discord.Discord_main import run_discord
from IO.IO_main import run_io
from Database.Database_main import run_database
from WebUI.WebUI_main import run_webui
from Chatbot.Chatbot_main import run_ai

from lib.Service_Runner import ServiceRunner

async def run_ui():
    twitch:dict[str, Awaitable] = {"TWITCH":run_twitch}
    tts:dict[str, Awaitable] = {"TTS":run_tts}
    discord:dict[str, Awaitable] = {"DISCORD":run_discord}
    chatbot:dict[str, Awaitable] = {"CHATBOT":run_ai}
    io:dict[str, Awaitable] = {"IO":run_io}
    webui:dict[str, Awaitable] = {"WEBUI":run_webui}
    database:dict[str, Awaitable] = {"DATABASE":run_database}
    
    all_mains:dict[str, Awaitable] = {
        **twitch,
        **tts,
        **discord,
        **chatbot,
        **io,
        **webui,
        **database,
    }

    start_mains:dict[str, Awaitable] = {
        **twitch,
        **database,
        **webui,
        **tts,
        **discord,
    }
    runner:ServiceRunner = ServiceRunner(all_mains=all_mains, start_mains=start_mains)

    while not runner.shutting_down_ui:
        await asyncio.sleep(3)
    return

if __name__ == "__main__":
    asyncio.run(run_ui())