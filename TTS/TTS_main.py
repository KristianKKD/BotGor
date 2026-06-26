import time
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment, find_port
from lib.API_Comms import join_listeners

from TTS.TTS_API import TTSService
from TTS.TTS_Engines.TTS_Base import TextToSpeechBase
from TTS.TTS_Engines.TTS_System import SystemTTS
from TTS.TTS_Engines.TTS_ElevenLabs import ElevenLabsTTS
from TTS.TTS_Handler import TTS_Handler


async def handle_input(tts:TTS_Handler):
    while True:
        async def handle_exit(_):
            return False

        async def stop_tts(_):
            tts.stop_audio()
            return True

        async def manual_tts(content):
            tts.speak(text=content, user="UIGor")
            return True
        
        commands = {
            "exit": handle_exit,
            "tts": manual_tts,
            "stoptts": stop_tts,
        }

        while True:
            user_input:str = str(await asyncio.to_thread(input, "Enter input:\n")).strip()
            cmd:str = user_input.lower().strip()
            arg:str = ""

            if ':' in user_input:
                cmd, arg = user_input.split(':', 1)

            if cmd in commands:
                if len(arg) > 0:
                    should_continue = await commands[cmd](arg)
                else:
                    should_continue = await commands[cmd]()

                if should_continue is False:
                    break
                continue

            print("Invalid input:" + user_input)
    return

async def main():
    load_environment()
    
    tts_engine:TextToSpeechBase = SystemTTS(id=0)
    #tts_engine:TextToSpeechBase = ElevenLabsTTS(api_key=os.environ["ELEVEN_LABS_KEY"], voice="xJ6quMToF3QzDncP3TLF", model_id="")
    
    tts_handler:TTS_Handler = TTS_Handler(engine = tts_engine)
    tts_service:TTSService = TTSService(tts_handler=tts_handler)

    listeners:dict[str, str] = join_listeners(port=tts_service.port)
    discord_port:int = find_port("DISCORD")
    if discord_port in listeners.values():
        tts_handler.toggle_discord(use_discord=True)
    
    asyncio.create_task(handle_input(tts_handler))
    while tts_service and not tts_service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(main())