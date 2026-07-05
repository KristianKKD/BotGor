import warnings
# warnings.filterwarnings("ignore", category=FutureWarning)

from RealtimeTTS import TextToAudioStream, SystemEngine
from TTS.TTS_Engines.TTS_Base import TTS_Base

class TTS_System(TTS_Base):
    def __init__(self, id:int, api_key:str="", voice:str="", model_id:str=""):
        super().__init__(id=id, api_key=api_key, voice=voice)
        return

    def setup_engine(self, api_key:str="", voice:str="", model_id:str=""):
        self.stream = TextToAudioStream(SystemEngine())
        return

    def generate_audio(self, audio_path:str, text:str):
        self.stream.feed(text)
        self.stream.play(output_wavfile=audio_path, muted=True)
        return

    def play_audio(self, audio_path:str, text:str):
        self.stream.feed(text)
        self.stream.play()
        return
    
    def stop_audio(self):
        self.stream.stop()
        return
    