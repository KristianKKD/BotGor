import os
import warnings

from typing import Any

from lib.API_Comms import post
from lib.Environment import find_port

from abc import ABC, abstractmethod

warnings.filterwarnings("ignore", category=FutureWarning)

class TTS_Base(ABC):
    def __init__(self, id:int=0, api_key:str="", voice:str="", model_id:str=""):
        print(f"Creating TTS instance of ID: {id}")

        self.id:int = id
        self.voice:str = voice
        self.model_id:str = model_id
        self.api_key = api_key

        self.setup_engine(api_key, voice)
        return

    def clone(self, new_id:int, voice:str):
        return self.__class__(
            id=new_id,
            api_key=self.api_key,
            voice=voice,
            model_id=self.model_id,
        )

    def __del__(self):
        #print("Deleting TTS instance")
        return
        
    def speak(self, text:str, user:str, output_file:bool) -> str:
        print(f"{user} said:{text}")

        audio_filename:str = f"output{str(self.id)}.wav"
        audio_path:str = os.path.join(os.getcwd(), 'audio', audio_filename)

        audio_dir:str = os.path.dirname(audio_path)
        os.makedirs(audio_dir, exist_ok=True)

        if output_file:
            self.generate_audio(audio_path=audio_path, text=text)
        else:
            self.play_audio(audio_path=audio_path, text=text)

        return audio_path

    @abstractmethod
    def stop_audio(self):
        """Stop TTS engine from outputting audio. Must be implemented by subclasses"""
        return

    @abstractmethod
    def get_voices(self) -> list[str]:
        """Print the available voices. Must be implemented by subclasses"""
        return
    
    @abstractmethod
    def select_voice(self, voice:str) -> list[str]:
        """Set the voice for future TTS audio. Must be implemented by subclasses"""
        return

    @abstractmethod
    def setup_engine(self, api_key:str, voice:str, model_id:str=""):
        """Initialize the TTS engine. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def generate_audio(self, audio_path:str, text:str) -> str:
        """Generate audio file from text. Must be implemented by subclasses."""
    
    @abstractmethod
    def play_audio(self, audio_path:str, text:str):
        """Play the generated audio. Must be implemented by subclasses."""
        pass
