import discord
from discord.ext import commands
from discord.client import VoiceClient

#VOICE_CHANNEL_ID = 1416079575628251167 #DiscGor stream
#VOICE_CHANNEL_ID = 471406637643464724 #kami weebs
#VOICE_CHANNEL_ID = 1201274493289648239 #kami chamber
VOICE_CHANNEL_ID = 389460211666255882 #kami f

class DiscordBot(commands.Bot): 
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        super().__init__(
            command_prefix="!",
            intents=intents
        )
        self.play_queue:list[str] = []
        self.playing:bool = False
        self.voice_connected:bool = False

    async def on_ready(self):
        print(f"Bot connected as: {str(self.user)}")
        for guild in self.guilds:
            channel = guild.get_channel(VOICE_CHANNEL_ID)
            if channel:
                break
        
        if channel and isinstance(channel, discord.VoiceChannel):
            try:
                await channel.connect()
                self.voice_connected = True
                print("Joined voice channel: " + str(channel.name))
            except Exception as e:
                print("Failed to connect to voice channel:", type(e).__name__, e)
        else:
            print("Voice channel not found or not a voice channel.")

    async def queue_play(self, file_path:str):
        def play_callback(err):
            if len(self.play_queue) > 0:
                self.play_queue.pop(0)

            if err:
                print("Failed callback, RIP")
                return

            if (len(self.play_queue) > 0):
                play()
            else:
                self.playing = False

        def play():
            self.playing = True

            voice_client : VoiceClient = self.voice_clients[0]
            try:
                file = self.play_queue[0]
                source = discord.FFmpegPCMAudio(file)
                voice_client.play(source=source, after=play_callback)
                #print("Playing " + file)
                
            except Exception as e:
                print("Error playing file: " + str(e))

        #play if nothing is going on, otherwise queue it
        if file_path is not None:
            self.play_queue.append(file_path)
        if not self.playing:
            play()

    async def stop_tts(self):
        print("Stopping TTS playback and clearing queue")
        self.play_queue = []
        if not self.voice_clients:
            return
        voice_client : VoiceClient = self.voice_clients[0]
        if voice_client.is_playing():
            voice_client.stop()

    async def disconnect(self):
        print("Disconnecting from VC")
        if not self.voice_clients:
            return
        guild = self.guilds[0]
        channel = guild.get_channel(VOICE_CHANNEL_ID)
        if channel and isinstance(channel, discord.VoiceChannel):
            voice_client = guild.voice_client
            await voice_client.disconnect()