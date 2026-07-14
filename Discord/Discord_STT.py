import io
import time
import wave
import asyncio
import threading
from threading import Event, Thread
from collections import deque

from discord import User
from discord.ext import voice_recv
from discord.ext.voice_recv import VoiceRecvClient
from discord.opus import Decoder

from STT.STT_Handler import STT_Handler
from lib.Broadcaster import Broadcaster

from dataclasses import dataclass

MIN_TOTAL_SPEAK_TIME_S:float = 0.6

class UserState:
    def __init__(self, discord_user:User):
        self.discord_user:User = discord_user
        self.username:str = self.discord_user.display_name

        self.audio:list[(float, bytes)] = []

        self.stop_event:Event = Event()
        self.thread:Thread = None

        self.transcribed:str = ""
        return

class Discord_STT():
    def __init__(self, voice_client:VoiceRecvClient, stt:STT_Handler, broadcaster:Broadcaster):
        print("Starting audio receiver...")

        self.voice_client:VoiceRecvClient = voice_client
        self.stt:STT_Handler = stt
        self.broadcaster:Broadcaster = broadcaster

        self.user_states:dict[str,UserState] = {}
        self._state_lock = threading.Lock()

        self.broadcast_queue:deque[dict[str, str]] = deque(dict[str, str])

        self.start_audio_receive()
        asyncio.ensure_future(self.start_broadcasting_queue())
        return

    def __del__(self):
        for user_state in self.user_states.values():
            if user_state.stop_event is not None:
                user_state.stop_event.set()

        for user_state in list(self.user_states.values()):
            if user_state.thread is not None and user_state.thread.is_alive():
                user_state.thread.join(timeout=1)
        return

    async def start_broadcasting_queue(self):
        while True:
            if len(self.broadcast_queue) > 0:
                message:dict[str, str] = self.broadcast_queue.popleft()
                self.broadcaster.broadcast(content=message)
            await asyncio.sleep(1)
        return

    def opus_to_wav(self, frames:list[bytes]) -> bytes:
        sample_rate = Decoder.SAMPLING_RATE
        channels = Decoder.CHANNELS
        sample_width = 2

        decoder = Decoder()
        pcm_chunks:list[bytes] = []
        for frame in frames:
            try:
                pcm_chunks.append(decoder.decode(frame, fec=False))
            except Exception:
                pass  # skip malformed frames

        if not pcm_chunks:
            return b""

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(pcm_chunks))
        return buffer.getvalue()

    def _watch_user(self, user_state:UserState):
        # print(f"{user_state.username} is speaking...")
        while not user_state.stop_event.is_set():
            speaking:bool = self.voice_client.get_speaking(member=user_state.discord_user)

            if not speaking:
                total_time_speaking_s, audio = filter_small_noises(user_audio=user_state.audio)

                #print(f"{user_state.username} stopped talking...")
                with self._state_lock:
                    self.user_states.pop(user_state.username, None)

                if total_time_speaking_s > MIN_TOTAL_SPEAK_TIME_S:
                    wav_data = self.opus_to_wav(frames=audio)
                    if wav_data:
                        self.broadcast_queue.append(self.stt.speech_to_text_json(audio_data=wav_data, user=user_state.username))
                return
            

            time.sleep(0.025)
        return

    def start_audio_receive(self):
        def voice_callback(user:User, data:voice_recv.VoiceData):
            username:str = user.display_name
            opus_frame:bytes = data.opus
            if not opus_frame:
                return

            with self._state_lock:
                user_state = self.user_states.get(username)
                if user_state is None:
                    user_state = UserState(discord_user=user)
                    thread:Thread = Thread(target=self._watch_user, args=(user_state,), daemon=True)
                    user_state.thread = thread
                    self.user_states[username] = user_state
                    thread.start()

                current_time:float = time.perf_counter()
                user_state.audio.append((current_time, opus_frame))
            return

        self.voice_client.listen(voice_recv.BasicSink(voice_callback, decode=False))
        print("Listening via receiver...")
        return


def filter_small_noises(user_audio:list[float, bytes]) -> tuple[float, list[bytes]]:
    """ 
    aggregate "chunks" of audio data,
    filter small chunks,
    add up total time,
    return filtered time and audio,
    """

    @dataclass
    class AudioChunk:
        time:float
        audio:list[bytes]

    times:list[float] = [frame[0] for frame in user_audio]
    audio:list[bytes] = [frame[1] for frame in user_audio]

    MAX_TIME_BETWEEN_FRAME_S:float = 0.2 # Too much time has passed since last audio for this to be speaking
    MIN_CHUNK_TIME_S:float = 0.2 # Minimum audio time to track

    audio_chunks:list[AudioChunk] = [] # List of aggregated audio frames per time chunk

    # Aggregate times into chunks, seperated by MAX_TIME_BETWEEN_FRAME
    chunk_time_s:float = 0
    last_chunk_index:int = 0
    for index, time in enumerate(times[1:]):
        last_time:float = times[index] # Index is naturally +1 as we start at +1 in loop
        relative_time_s:float = time - last_time

        # Is not part of the same chunk as the last audio frame
        if relative_time_s > MAX_TIME_BETWEEN_FRAME_S or index == len(times)-2:
            # Filter chunk too small
            if chunk_time_s > MIN_CHUNK_TIME_S:
                audio_chunks.append(AudioChunk(time=chunk_time_s, audio=times[last_chunk_index:index]))
            
            # Reset chunk
            last_chunk_index = index
            chunk_time_s = 0
        
        chunk_time_s += relative_time_s

    total_time_s:float = sum(chunk.time for chunk in audio_chunks)

    return total_time_s, audio