import asyncio
from collections import deque 
import time

from lib.API_Comms import post
from lib.Environment import find_port
from lib.Broadcaster import Broadcaster
from TTS.TTS_Engines.TTS_Base import TTS_Base

class TTS_Message:
    def __init__(self, engine:TTS_Base, text:str, user:str):
        self.engine:TTS_Base = engine
        self.text:str = text
        self.user:str = user
        return
    
    def play_message(self, output_file:bool):
        return self.engine.speak(text=self.text, user=self.user, output_file=output_file)

    def stop_audio(self):
        self.engine.stop_audio()
        return

class TTS_Handler():
    def __init__(self, engine:TTS_Base, broadcaster:Broadcaster=None):
        super().__init__()

        self._tts_in_progress:deque[TTS_Message] = deque([])
        self._tts_count:int = 0
        self.engine:TTS_Base = engine
        self.processing:bool = False
        self.use_discord:bool = False
        self.broadcaster:Broadcaster = broadcaster
        return

    async def _speak_loop(self):
        while(len(self._tts_in_progress) > 0):
            tts:TTS_Message = self._tts_in_progress.popleft()

            file_path:str = tts.play_message(output_file=self.use_discord)
            if self.use_discord and self.broadcaster:
                self.broadcaster.broadcast(msg={"path":file_path})

        self.processing = False
        return

    async def speak(self, text:str, user:str):
        self._tts_count += 1
        msg_engine:TTS_Base = self.engine.clone(new_id=self._tts_count)

        tts:TTS_Message = TTS_Message(engine=msg_engine, text=text, user=user)
        
        self._tts_in_progress.append(tts)

        if not self.processing:
            self.processing = True
            asyncio.create_task(self._speak_loop())
        return

    async def stop_audio(self):
        print("Stopping all TTS messages")

        tts:TTS_Message
        for tts in self._tts_in_progress:
            tts.stop_audio()
        if self.use_discord:
            post(msg="stop", port=find_port("DISCORD"))

        self._tts_in_progress.clear()
        return
