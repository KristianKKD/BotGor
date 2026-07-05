from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import warnings
import wave
from TTS.TTS_Engines.TTS_Base import TTS_Base
warnings.filterwarnings("ignore", category=FutureWarning)

class ElevenLabsTTS(TTS_Base):
    def __init__(self, id:int, api_key:str="", voice:str="", model_id:str=""):
        super().__init__(id=id, api_key=api_key, voice=voice, model_id=model_id)
        return

    def setup_engine(self, api_key:str, voice:str, model_id:str=""):
        self.elevenlabs = ElevenLabs(
            api_key=api_key,
        )

        if voice == "" : self.voice = "JBFqnCBsd6RMkjVDRZzb"
        if model_id == "" : self.model_id = "eleven_flash_v2_5"
        return

    def generate_audio(self, audio_path:str, text:str):
        audio_iterator = self.elevenlabs.text_to_speech.convert(
            text=text,
            voice_id=self.voice,
            model_id=self.model_id,
            output_format="mp3_44100_128",
        )

        # Combine the audio bytes from the iterator
        audio_data:bytes = b"".join(audio_iterator)

        # Save the audio data into a .wav file
        with wave.open(audio_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # Sample width in bytes (16-bit audio)
            wav_file.setframerate(44100)  # Sample rate
            wav_file.writeframes(audio_data)
        return

    def play_audio(self, audio_path:str, text:str):
        audio_stream = self.elevenlabs.text_to_speech.stream(
            text=text,
            voice_id=self.voice,
            model_id=self.model_id,
            output_format="mp3_44100_128",
        )

        stream(audio_stream)
        return

    def stop_audio(self):
        return
