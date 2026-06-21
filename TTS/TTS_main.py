import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment, find_port
from lib.API_Comms import join_listeners

from TTS.TTS_API import TTSService
from TTS.TTS_Base import TextToSpeechBase
from TTS.TTS_System import SystemTTS
from TTS.TTS_ElevenLabs import ElevenLabsTTS

if __name__ == "__main__":
    load_environment()
    
    tts_engine:TextToSpeechBase = SystemTTS()
    #tts_engine:TextToSpeechBase = ElevenLabsTTS(api_key=os.environ["ELEVEN_LABS_KEY"], voice="xJ6quMToF3QzDncP3TLF", model_id="")
    
    tts_service:TTSService = TTSService(tts_engine=tts_engine)

    listeners:dict[str, str] = join_listeners(port=tts_service.port)
    discord_port:int = find_port("DISCORD")
    if discord_port in listeners.values():
        tts_service.discord_enabled = True
        
    while tts_service and not tts_service.shutdown:
        time.sleep(5)