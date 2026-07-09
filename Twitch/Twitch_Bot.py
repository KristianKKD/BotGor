import os
import asyncio

import twitchio
from twitchio.ext.commands import Bot, AutoBot, CommandErrorPayload
from twitchio.ext.commands.exceptions import CommandNotFound
from twitchio import ChatMessage, eventsub
from twitchio import authentication, eventsub

from lib.TwitchMsg import TwitchMsg
from lib.Broadcaster import Broadcaster

#http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot&force_verify=true
#http://localhost:4343/oauth?scopes=Amanage%3Abroadcast+moderator%3Aread%3Ashield_mode+moderator%3Amanage%3Aannouncements+channel%3Aread%3Agoals+moderator%3Aread%3Aautomod_settings+moderator%3Amanage%3Aautomod+whispers%3Aedit+moderator%3Aread%3Achat_messages+user%3Aread%3Awhispers+channel%3Amoderate+moderator%3Aread%3Abanned_users+moderator%3Aread%3Amoderators+channel%3Aread%3Astream_key+moderator%3Amanage%3Aunban_requests+analytics%3Aread%3Aextensions+moderator%3Amanage%3Ashoutouts+chat%3Aedit+moderator%3Aread%3Awarnings+analytics%3Aread%3Agames+channel%3Aread%3Asubscriptions+user%3Amanage%3Achat_color+moderator%3Amanage%3Aautomod_settings+moderator%3Aread%3Achat_settings+moderator%3Aread%3Ablocked_terms+channel%3Aread%3Aguest_star+moderator%3Aread%3Avips+user%3Awrite%3Achat+moderation%3Aread+moderator%3Aread%3Asuspicious_users+channel%3Amanage%3Aredemptions+moderator%3Amanage%3Aguest_star+channel%3Aedit%3Acommercial+user%3Aread%3Aemotes+user%3Abot+channel%3Aread%3Avips+user%3Aread%3Afollows+channel%3Aread%3Apolls+channel%3Amanage%3Aads+user%3Aedit%3Abroadcast+channel%3Amanage%3Araids+user%3Aread%3Asubscriptions&force_verify=true

class Twitch_Bot(AutoBot):
    def __init__(self, filtered_words:list[str], broadcaster:Broadcaster, prefix:str=""):
        USER_ID = os.environ["TWITCH_KRABGOR_ACCOUNT_ID"]
        BOT_ID = os.environ["TWITCH_BOTGOR_ACCOUNT_ID"]
        subs:eventsub.SubscriptionPayload = [
            eventsub.ChatMessageSubscription(broadcaster_user_id=USER_ID, user_id=BOT_ID),
            eventsub.StreamOnlineSubscription(broadcaster_user_id=USER_ID),
        ]

        super().__init__(
            client_id=os.environ["TWITCH_CLIENT_ID"],
            client_secret=os.environ["TWITCH_SECRET"],
            bot_id=BOT_ID,
            owner_id=USER_ID,
            prefix=prefix,
            subscriptions=subs,
            force_subscribe=True
        )

        self.broadcaster:Broadcaster = broadcaster
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

    async def login(self, *, token:str | None = None, load_tokens:bool = True, save_tokens:bool = True):
        print("Logging in to bot...")
        await super().login(token=token, load_tokens=load_tokens, save_tokens=save_tokens)
        print("Logged in...")
        return

    async def setup_hook(self):
        print("Subscribing to channel...")
        await self.add_component(ListenerComponent(self, filtered_words=self.filtered_words, broadcaster=self.broadcaster))
        return

    async def event_ready(self):
        print(f"Successfully logged in as: {self.bot_id}")
        return

    async def event_command_error(self, payload:CommandErrorPayload) -> None:
        if isinstance(payload.exception, CommandNotFound):
            return
        raise payload.exception
    
class ListenerComponent(twitchio.ext.commands.Component):
    def __init__(self, bot:Bot, filtered_words:list[str], broadcaster:Broadcaster) -> None:
        self.bot:Bot = bot
        self.filtered_words:list[str] = filtered_words
        self.broadcaster:Broadcaster = broadcaster
        print("Creating listener component!")
        return

    @twitchio.ext.commands.Component.listener()
    async def event_message(self, message:ChatMessage):
        def has_slurs(message:str) -> bool:
            return any(word in message.lower() for word in self.filtered_words)
        
        user:str = message.chatter.display_name
        content:str = message.text
        if has_slurs(content):
            print(f"Message filtered from user: {user}")
            return
        
        if not content.startswith(self.bot._get_prefix):
            return

        msg:TwitchMsg = TwitchMsg(user=user, content=content)
        print(f"Message created: User: {user} Message: {content}")

        if self.broadcaster:
            self.broadcaster.broadcast(msg=msg.to_json())
        return