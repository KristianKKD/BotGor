from RealtimeTTS import TextToAudioStream, SystemEngine
import asyncio
import warnings
from TTS.TTS_Engines.TTS_Base import TextToSpeechBase
warnings.filterwarnings("ignore", category=FutureWarning)

class SystemTTS(TextToSpeechBase):
    def __init__(self, id:int, api_key:str="", voice:str="", model_id:str=""):
        super().__init__(id=id, api_key=api_key, voice=voice)
        return

    def setup_engine(self, api_key:str="", voice:str="", model_id:str=""):
        self.engine = SystemEngine()
        self.stream = TextToAudioStream(self.engine)
        return

    async def generate_audio(self, audio_path:str, text:str):
        self.stream.feed(text)
        await asyncio.to_thread(self.stream.play, output_wavfile=audio_path, muted=True)
        return

    async def play_audio(self, audio_path:str, text:str):
        self.stream.feed(text)
        await asyncio.to_thread(self.stream.play)
        return
    
    def stop_audio(self):
        self.stream.stop()
        return
    