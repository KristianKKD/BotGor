import os
import warnings

from lib.API_Comms import post
from lib.Environment import find_port

from abc import ABC, abstractmethod

warnings.filterwarnings("ignore", category=FutureWarning)

class TextToSpeechBase(ABC):
    def __init__(self, id:int, api_key:str="", voice:str="", model_id:str=""):
        print("Creating TTS instance")

        self.id:int = id
        self.voice:str = voice
        self.model_id:str = model_id
        self.api_key = api_key

        self.setup_engine(api_key, voice)
        return

    def clone(self, new_id:int):
        return self.__class__(
            new_id,
            api_key=self.api_key,
            voice=self.voice,
            model_id=self.model_id,
        )

    def __deepcopy__(self, memo):
        new = self.clone(self.id)
        memo[id(self)] = new
        return new

    def __del__(self):
        #print("Deleting TTS instance")
        return
        
    async def speak(self, text:str, user:str, use_discord:bool):
        print(f"{user} said:{text}")

        audio_filename:str = f"output{str(self.id)}.wav"
        audio_path:str = os.path.join(os.getcwd(), 'audio', audio_filename)

        if use_discord:
            await self.generate_audio(audio_path=audio_path, text=text)
            post(msg="play", port=find_port("DISCORD"), json={"audio_path":audio_path})
        else:
            await self.play_audio(audio_path=audio_path, text=text)

        return

    @abstractmethod
    async def stop_audio(self):
        """Stop TTS engine from outputting audio. Must be implemented by subclasses"""
        return

    @abstractmethod
    async def setup_engine(self, api_key:str, voice:str, model_id:str=""):
        """Initialize the TTS engine. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def generate_audio(self, audio_path:str, text:str):
        """Generate audio file from text. Must be implemented by subclasses."""
    
    @abstractmethod
    async def play_audio(self, audio_path:str, text:str):
        """Play the generated audio. Must be implemented by subclasses."""
        pass
