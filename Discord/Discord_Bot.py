import asyncio
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands, voice_recv
from discord.ext.voice_recv import VoiceRecvClient

from collections import deque 

from STT.STT_Handler import STT_Handler
from Discord.Discord_STT import Discord_STT
from lib.Broadcaster import Broadcaster

# https://github.com/imayhaveborkedit/discord-ext-voice-recv

class Discord_Bot(commands.Bot): 
    def __init__(self, channel_id:int, broadcaster:Broadcaster, stt:STT_Handler | None=None):
        intents = discord.Intents.default()
        intents.voice_states = True

        commands.Bot.__init__(
            self=self,
            command_prefix="!",
            intents=intents
        )
        
        self.play_queue:deque[str] = deque([])
        self.playing:bool = False
        self.channel_id:int = channel_id

        self.broadcaster:Broadcaster = broadcaster
        self.stt:STT_Handler = stt
        self.vc:VoiceRecvClient = None
        self.receiver:Discord_STT = None
        return

    def __del__(self):
        asyncio.run(self.disconnect())
        if self.stt:
            self.stt.__del__()
        if self.receiver:
            self.receiver.__del__()
        return

    async def on_ready(self):
        print(f"Bot connected as: {self.user}")
        print(f"Voice clients at ready: {self.voice_clients}")

        for guild in self.guilds:
            channel = guild.get_channel(self.channel_id)
            if channel:
                break

        if guild.voice_client:
            print("Already connected to voice channel")
            return

        if channel and isinstance(channel, discord.VoiceChannel):
            try:
                self.vc:VoiceRecvClient = await channel.connect(cls=voice_recv.VoiceRecvClient)
                print(f"Joined voice channel: {channel.name}")
                if self.stt:
                    self.receiver:Discord_STT = Discord_STT(voice_client=self.vc, stt=self.stt, broadcaster=self.broadcaster)
            except Exception as e:
                print("Failed to connect to voice channel:", type(e).__name__, e)
        else:
            print("Voice channel not found or not a voice channel.")
        return

    async def queue_play(self, file_path:str):
        def play_callback(err):
            if err:
                print("Failed callback, RIP")
                return

            if (len(self.play_queue) > 0):
                play()
            else:
                self.playing = False
            return

        def play():
            self.playing = True
            try:
                file:str = self.play_queue.popleft()
                source:FFmpegPCMAudio = FFmpegPCMAudio(file)
                self.vc.play(source=source, after=play_callback)
            except Exception as e:
                print("Error playing file: " + str(e))
            return

        #play if nothing is going on, otherwise queue it
        if file_path is not None:
            self.play_queue.append(file_path)
        if not self.playing:
            play()
        return

    async def stop_audio(self):
        print("Stopping TTS playback and clearing queue")
        self.play_queue.clear()
        if not self.vc:
            return
        if self.vc.is_playing():
            self.vc.stop()
        return

    async def disconnect(self):
        print("Disconnecting from VC")
        if not self.voice_clients:
            return
        guild = self.guilds[0]
        channel = guild.get_channel(self.channel_id)
        if channel and isinstance(channel, discord.VoiceChannel):
            client = guild.voice_client
            await client.disconnect()
        return