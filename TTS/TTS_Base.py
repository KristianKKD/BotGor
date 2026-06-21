import os
import warnings

from lib.API_Comms import post
from lib.Environment import find_port

from abc import ABC, abstractmethod

warnings.filterwarnings("ignore", category=FutureWarning)

_tts_id_counter:int = 0

class TextToSpeechBase(ABC):
    text:str = ""
    id:int = 0
    voice:str = ""
    model_id:str = ""

    def __init__(self, api_key:str="", voice:str="", model_id:str=""):
        print("Creating TTS instance")

        self.voice:str = voice
        self.model_id:str = model_id

        global _tts_id_counter
        self.id = _tts_id_counter
        _tts_id_counter += 1

        self.setup_engine(api_key, voice)
        return

    def __del__(self):
        #print("Deleting TTS instance")
        return
        
    async def speak(self, text:str, user:str, use_discord:bool):
        self.text = text
        print(f"{user} said:{text}")

        audio_filename:str = "output" + str(self.id) + ".wav"
        audio_path:str = os.path.join(os.getcwd(), 'audio', audio_filename)

        if use_discord:
            await self.generate_audio(audio_path)
            post(msg="play", data=audio_path, port=find_port("DISCORD"))
        else:
            await self.play_audio(audio_path)

        return

    def stop_audio(self):
        print("Stopping TTS message: " + self.text)
        self.stream.stop()
        if self.discord_bot is not None:
            self.discord_bot.stop_tts()
        return
    
    @abstractmethod
    async def setup_engine(self, api_key:str, voice:str, model_id:str=""):
        """Initialize the TTS engine. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def generate_audio(self, audio_path:str):
        """Generate audio file from text. Must be implemented by subclasses."""
    
    @abstractmethod
    async def play_audio(self, audio_path:str):
        """Play the generated audio. Must be implemented by subclasses."""
        pass
