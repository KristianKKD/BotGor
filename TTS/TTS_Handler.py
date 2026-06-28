import asyncio
import copy

from lib.API_Comms import post
from lib.Environment import find_port
from TTS.TTS_Engines.TTS_Base import TextToSpeechBase
from TTS.TTS_API import TTS_Service

class TTS_Handler(TTS_Service):
    def __init__(self, engine:TextToSpeechBase):
        super().__init__()

        self.tts_in_progress:list[TextToSpeechBase] = []
        self.engine:TextToSpeechBase = engine
        self.tts_count:int = 0
        return

    def speak(self, text:str, user:str):
        tts:TextToSpeechBase = copy.deepcopy(self.engine, memo={id:self.tts_count})
        self.tts_count += 1
        self.tts_in_progress.append(tts)

        # Run in background so no blocking
        async def speak_and_cleanup():
            await tts.speak(text=text, 
                            user=user,
                            use_discord=self.use_discord
                            )
            if tts in self.tts_in_progress:
                self.tts_in_progress.remove(tts)

        asyncio.create_task(speak_and_cleanup())
        return

    async def stop_audio(self):
        print("Stopping all TTS messages")

        tts:TextToSpeechBase
        for tts in self.tts_in_progress:
            tts.stop_audio()
        if self.use_discord:
            post(msg="stop", port=find_port("DISCORD"))

        self.tts_in_progress = []
        return
