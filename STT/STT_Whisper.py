import io
from faster_whisper import WhisperModel

MODEL:str = "large-v3-turbo"


class WhisperTranscriber():
    def __init__(self):
        self.model:WhisperModel = WhisperModel(MODEL, device="cuda", compute_type="float16")
        return

    def transcribe(self, audio_data:bytes) -> str:
        segments, _ = self.model.transcribe(
            io.BytesIO(audio_data),
            language="en",
            # beam_size=3,
            # best_of=3,
            # condition_on_previous_text=False,
            # no_speech_threshold=0.15,
            # vad_filter=False,
            word_timestamps=False,
        )
        recognized_audio:str = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
        return recognized_audio
