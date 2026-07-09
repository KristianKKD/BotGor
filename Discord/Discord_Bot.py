import discord
from discord import FFmpegPCMAudio
from discord.ext.commands import Bot
from discord.client import VoiceClient
from collections import deque 

class Discord_Bot(Bot): 
    def __init__(self, channel_id:int):
        intents = discord.Intents.default()
        intents.voice_states = True
        Bot.__init__(
            self=self,
            command_prefix="!",
            intents=intents
        )
        
        self.play_queue:deque[str] = deque([])
        self.playing:bool = False
        self.channel_id:int = channel_id
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
                await channel.connect()
                self.voice_client:VoiceClient = self.voice_clients[0]
                print(f"Joined voice channel: {channel.name}")
            except Exception as e:
                print("Failed to connect to voice channel:", type(e).__name__, e)
        else:
            print("Voice channel not found or not a voice channel.")
        return

    async def on_disconnect(self):
        print("Discord bot disconnected from gateway")
        return

    async def on_resumed(self):
        print("Discord bot resumed gateway session")
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
                self.voice_client.play(source=source, after=play_callback)
            except Exception as e:
                print("Error playing file: " + str(e))
            return

        #play if nothing is going on, otherwise queue it
        if file_path is not None:
            self.play_queue.append(file_path)
        if not self.playing:
            play()
        return

    async def stop_tts(self):
        print("Stopping TTS playback and clearing queue")
        self.play_queue.clear()
        if not self.voice_client:
            return
        if self.voice_client.is_playing():
            self.voice_client.stop()
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