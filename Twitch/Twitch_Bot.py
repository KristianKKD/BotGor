import os

from twitchio.ext.commands import Bot
from twitchio.message import Message

from lib.TwitchMsg import TwitchMsg
from Twitch.Twitch_API import Twitch_Service

class Twitch_Bot(Bot, Twitch_Service):
    def __init__(self, filtered_words:list[str]):
        Twitch_Service.__init__(self)

        Bot.__init__(
            self=self,
            token=os.environ["TWITCH_TOKEN"],
            client_id=os.environ["TWITCH_CLIENT_ID"],
            nick='BotGor',
            prefix='!',
            initial_channels=['KrabGor']
        )

        self.filtered_words:list[str] = filtered_words
        return

    async def connect(self):
        await super().connect()
        print ("Bot connected. Listening for messages...")
        return

    async def event_message(self, message:Message):
        def has_slurs(message:str) -> bool:
            return any(word in message.lower() for word in self.filtered_words)
        
        user:str = message.author.name
        content:str = message.content
        if has_slurs(content):
            return

        msg:TwitchMsg = TwitchMsg(user=user, content=content)
        print(f"Message created: User: {user} Message: {content}")
        self.broadcaster.broadcast(msg=msg.to_json())
        return