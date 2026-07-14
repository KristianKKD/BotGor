from speech_recognition import AudioData, Microphone, Recognizer

class AudioRecorder():
    def __init__(self):
        print("Loading audio transcriber...")
        print("Setting mic settings...")
        self.recognizer:Recognizer = Recognizer()
        self.mic:Microphone = Microphone()
        self.calibrate_microphone()
        return

    def settings(self):
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 180
        self.recognizer.pause_threshold = 0.4
        self.recognizer.non_speaking_duration = 0.2
        return

    def calibrate_microphone(self):
        with self.mic as source:
            print("Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print("Microphone calibrated.")
            return

    def record_audio(self) -> bytes:
        print("Recording microphone...")
        with self.mic as source:
            audio:AudioData = self.recognizer.listen(source)
        return audio.get_wav_data()
