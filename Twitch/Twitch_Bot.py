import os
import asyncio

import twitchio
from twitchio.ext.commands import Bot, AutoBot
from twitchio import ChatMessage, eventsub
from twitchio import authentication, eventsub


from lib.TwitchMsg import TwitchMsg
from Twitch.Msg_Broadcaster import broadcaster


#http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot&force_verify=true
#http://localhost:4343/oauth?scopes=Amanage%3Abroadcast+moderator%3Aread%3Ashield_mode+moderator%3Amanage%3Aannouncements+channel%3Aread%3Agoals+moderator%3Aread%3Aautomod_settings+moderator%3Amanage%3Aautomod+whispers%3Aedit+moderator%3Aread%3Achat_messages+user%3Aread%3Awhispers+channel%3Amoderate+moderator%3Aread%3Abanned_users+moderator%3Aread%3Amoderators+channel%3Aread%3Astream_key+moderator%3Amanage%3Aunban_requests+analytics%3Aread%3Aextensions+moderator%3Amanage%3Ashoutouts+chat%3Aedit+moderator%3Aread%3Awarnings+analytics%3Aread%3Agames+channel%3Aread%3Asubscriptions+user%3Amanage%3Achat_color+moderator%3Amanage%3Aautomod_settings+moderator%3Aread%3Achat_settings+moderator%3Aread%3Ablocked_terms+channel%3Aread%3Aguest_star+moderator%3Aread%3Avips+user%3Awrite%3Achat+moderation%3Aread+moderator%3Aread%3Asuspicious_users+channel%3Amanage%3Aredemptions+moderator%3Amanage%3Aguest_star+channel%3Aedit%3Acommercial+user%3Aread%3Aemotes+user%3Abot+channel%3Aread%3Avips+user%3Aread%3Afollows+channel%3Aread%3Apolls+channel%3Amanage%3Aads+user%3Aedit%3Abroadcast+channel%3Amanage%3Araids+user%3Aread%3Asubscriptions&force_verify=true

class KrabBot(AutoBot):
    def __init__(self, filtered_words:list[str]):
        super().__init__(
            client_id=os.environ["TWITCH_CLIENT_ID"],
            client_secret=os.environ["TWITCH_SECRET"],
            owner_id=os.environ["TWITCH_KRABGOR_ACCOUNT_ID"],
            bot_id=os.environ["TWITCH_BOTGOR_ACCOUNT_ID"],
            load_tokens=True,
            force_subscribe=True,
            prefix='',
        )
    
        self.filtered_words:list[str] = filtered_words

        return

    async def event_oauth_authorized(self, payload:authentication.UserTokenPayload):
        # Stores tokens in .tio.tokens.json by default; can be overriden to use a DB for example
        print("Authenticated!")
        await self.add_token(payload.access_token, payload.refresh_token)
        await self.save_tokens()

        if payload.user_id == self.bot_id:
            return

        chat = eventsub.ChatMessageSubscription(broadcaster_user_id=payload.user_id, user_id=self.bot_id)
        await self.multi_subscribe([chat])
        print("Listening to chat!")
        return

    async def run(self):
        print("Logging in to bot...")
        await super().run()
        print ("Bot connected. Listening for messages...")
        return

    async def setup_hook(self):
        print("Subscribing to channel...")
        await self.add_component(ListenerComponent(self))
        return

    async def event_ready(self):
        print(f"Successfully logged in as: {self.bot_id}")
        return

class ListenerComponent(twitchio.ext.commands.Component):
    def __init__(self, bot:Bot) -> None:
        self.bot:Bot = bot
        print("Creating listener component!")
        return

    @twitchio.ext.commands.Component.listener()
    async def event_message(self, message:ChatMessage):
        def has_slurs(message:str) -> bool:
            return any(word in message.lower() for word in self.bot.filtered_words)
        
        user:str = message.chatter.display_name
        content:str = message.text
        print(f"Message created: User: {user} Message: {content}")

        if has_slurs(content):
            return

        msg:TwitchMsg = TwitchMsg(user=user, content=content)
        asyncio.create_task(broadcaster.incoming_message(msg))
        return