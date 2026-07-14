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

async def run_tts(manual_input:bool=False):
    load_environment()
    
    tts_engine:TTS_Base = TTS_System(voice="Microsoft David Desktop - English (United States)")
    #old botgor: xJ6quMToF3QzDncP3TLF
    #tts_engine:TTS_Base = ElevenLabsTTS(api_key=os.environ["ELEVEN_LABS_KEY"], voice="mrQhZWGbb2k9qWJb5qeA")
    
    broadcaster:Broadcaster = Broadcaster(name="TTS")
    
    tts_handler:TTS_Handler = TTS_Handler(engine=tts_engine, broadcaster=broadcaster)
    service:TTS_Service = TTS_Service(tts=tts_handler, broadcaster=broadcaster, ui_enabled=manual_input)

    while not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_tts(manual_input=True))