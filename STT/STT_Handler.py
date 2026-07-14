from STT.STT_Whisper import WhisperTranscriber
from STT.STT_Recorder import AudioRecorder
from lib.API_Msgs import OUTPUT_MSG, USER

class STT_Handler():
    def __init__(self, model:WhisperTranscriber, recorder:AudioRecorder | None=None):
        self.model:WhisperTranscriber = model
        self.recorder:AudioRecorder = recorder
        return
    
    def speech_to_text(self, audio_data:bytes, user:str="User") -> str:
        text:str = self.model.transcribe(audio_data)
        print(f"{user}'s transcribed text: {text}")
        return text
    
    def record_speech_to_text(self) -> str:
        if not self.recorder:
            raise ValueError("No recorder for self recording!")
        
        audio_data:bytes = self.recorder.record_audio()
        return self.speech_to_text(audio_data=audio_data)
    
    def speech_to_text_json(self, audio_data:bytes, user:str="User") -> dict[str, str]:
        return {USER:user, OUTPUT_MSG:self.speech_to_text(audio_data=audio_data, user=user)}