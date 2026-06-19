import os
import asyncio

from twitchio.ext.commands import Bot
from twitchio.message import Message

from Core.SimpleMsg import SimpleMsg
from Core.Message_Routing import router

class KrabBot(Bot):
    def __init__(self, filtered_words:list[str]):
        super().__init__(
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
        msg = SimpleMsg(user=message.author.name, content=message.content)
        asyncio.create_task(router.incoming_message(msg))
        return