import time
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment
from lib.Broadcaster import Broadcaster

from TTS.TTS_Engines.TTS_Base import TTS_Base
from TTS.TTS_Engines.TTS_System import TTS_System
from TTS.TTS_Engines.TTS_ElevenLabs import ElevenLabsTTS
from TTS.TTS_Handler import TTS_Handler
from TTS.TTS_API import TTS_Service

async def handle_input(tts:TTS_Handler):
    while True:
        async def handle_exit(_):
            return False

        async def stop_tts(_):
            tts.stop_audio()
            return True

        async def manual_tts(content):
            await tts.speak(text=content, user="UIGor")
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
                    should_continue = await commands[cmd]("")

                if should_continue is False:
                    break
                continue

            print("Invalid input:" + user_input)
    return

async def main():
    load_environment()
    
    tts_engine:TTS_Base = TTS_System(id=0)
    #tts_engine:TextToSpeechBase = ElevenLabsTTS(api_key=os.environ["ELEVEN_LABS_KEY"], voice="xJ6quMToF3QzDncP3TLF", model_id="")
    
    broadcaster:Broadcaster = Broadcaster()
    tts_handler:TTS_Handler = TTS_Handler(engine=tts_engine, broadcaster=broadcaster)
    service:TTS_Service = TTS_Service(tts=tts_handler, broadcaster=broadcaster)

    asyncio.create_task(handle_input(tts=tts_handler))
    while not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(main())