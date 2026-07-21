import asyncio
from collections import deque 

from lib.Broadcaster import Broadcaster
from TTS.TTS_Engines.TTS_Base import TTS_Base
from lib.API_Msgs import PATH_MSG, STOP_MSG

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
        self.paused:bool = False

        self._voice:str = engine.voice

        return

    def set_voice(self, voice:str | int) -> str:
        try:
            voice_index:int = int(voice)
            voices:dict[str, str] = self.engine.get_voices()
            voice:str = voices[voice_index]
        except ValueError:
            pass

        self._voice = voice
        print(f"Changed voice to:{self._voice}")
        return self._voice

    async def _speak_loop(self):
        while(len(self._tts_in_progress) > 0):
            if self.paused:
                return
            
            tts:TTS_Message = self._tts_in_progress.popleft()

            file_path:str = tts.play_message(output_file=self.use_discord)
            if self.use_discord and self.broadcaster:
                self.broadcaster.broadcast(content={PATH_MSG:file_path})

        self.processing = False
        return

    async def speak(self, text:str, user:str):
        self._tts_count += 1
        msg_engine:TTS_Base = self.engine.clone(new_id=self._tts_count, voice=self._voice)

        tts:TTS_Message = TTS_Message(engine=msg_engine, text=text, user=user)
        
        self._tts_in_progress.append(tts)

        self._start_audio()
        return

    def pause_audio(self):
        print("Paused audio")
        self.paused = True
        return
    
    def resume_audio(self):
        print("Resumed audio")
        self.paused = False
        self._start_audio()
        return

    def _start_audio(self):
        if not self.processing and not self.paused:
            self.processing = True
            asyncio.create_task(self._speak_loop())
        return

    async def stop_audio(self):
        print(f"Stopping all TTS messages ({len(self._tts_in_progress)})")

        self.pause_audio()

        tts:TTS_Message
        for tts in self._tts_in_progress:
            tts.stop_audio()
        if self.use_discord:
            self.broadcaster.broadcast(content={}, msg=STOP_MSG)

        self._tts_in_progress.clear()
        return
