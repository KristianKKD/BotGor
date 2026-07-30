import os
import asyncio
from typing import Any

import twitchio
from twitchio.ext.commands import Bot, AutoBot, CommandErrorPayload
from twitchio.ext.commands.exceptions import CommandNotFound
from twitchio import eventsub, authentication
from twitchio import ChatMessage, WebsocketWelcome, SubscriptionRevoked, ChannelPointsAutoRedeemAdd, ChannelPointsRedemptionAdd

from lib.Broadcaster import Broadcaster
import Database.Database_API
from Database.Database_User import UserMsg, User
from lib.API_Msgs import CONTENT_KEY

#http://localhost:4343/oauth?scopes=channel%3Aread%3Aredemptions+user%3Aread%3Achat+user%3Awrite%3Achat+user%3Abot+channel%3Abot&force_verify=true

class Twitch_Bot(AutoBot):
    def __init__(self, filtered_words:list[str], broadcaster:Broadcaster, prefix:str=""):
        USER_ID = os.environ["TWITCH_KRABGOR_ACCOUNT_ID"]
        BOT_ID = os.environ["TWITCH_BOTGOR_ACCOUNT_ID"]
        subs:eventsub.SubscriptionPayload = [
            eventsub.ChatMessageSubscription(broadcaster_user_id=USER_ID, user_id=BOT_ID),
            eventsub.ChannelPointsAutoRedeemV2Subscription(broadcaster_user_id=USER_ID),
            eventsub.ChannelPointsRedeemAddSubscription(broadcaster_user_id=USER_ID)
        ]

        AutoBot.__init__(self=self,
            client_id=os.environ["TWITCH_CLIENT_ID"],
            client_secret=os.environ["TWITCH_SECRET"],
            bot_id=BOT_ID,
            owner_id=USER_ID,
            prefix=prefix,
            subscriptions=subs,
            force_subscribe=True,
        )

        self.broadcaster:Broadcaster = broadcaster
        self.filtered_words:list[str] = filtered_words
        return

    async def event_oauth_authorized(self, payload:authentication.UserTokenPayload):
        # Stores tokens in .tio.tokens.json by default; can be overriden to use a DB for example
        print("Authenticated!")
        await self.add_token(payload.access_token, payload.refresh_token)
        await self.save_tokens()
        print("Saved token!")
        return

    async def login(self, *, token:str | None = None, load_tokens:bool = True, save_tokens:bool = True):
        print("Logging in to bot...")
        try:
            await AutoBot.login(self=self, token=token, load_tokens=load_tokens, save_tokens=save_tokens)
            if not self.adapter._running:
                await self.adapter.run()
        except Exception as error:
            print(f"[TWITCH AUTH ERROR] Login failed: {error}")
            raise
        print("Logged in...")
        return

    async def setup_hook(self):
        print("Subscribing to channel...")
        await self.add_component(ListenerComponent(self, filtered_words=self.filtered_words, broadcaster=self.broadcaster))
        return

    async def event_ready(self):
        print(f"Successfully logged in as: {self.bot_id}")
        return

    async def event_websocket_welcome(self, payload:WebsocketWelcome):
        print(f"Successfully connected to channel")
        return

    async def event_subscription_revoked(self, payload:SubscriptionRevoked):
        print(f"[TWITCH AUTH WARNING] Subscription revoked")
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
        
        username:str = message.chatter.display_name
        content:str = message.text
        if has_slurs(content):
            print(f"Message filtered from user: {username}")
            return

        font:str = ""
        font_size:int = 0
        user_data:User = await Database.Database_API.get_user(username=username)
        if user_data:
            font = user_data.font
            font_size = user_data.font_size
        else:
            asyncio.create_task(Database.Database_API.add_user(User(name=username)))
        
        msg:UserMsg = UserMsg(name=username, content=content, font=font, font_size=font_size)
        print(f"Message created: {msg}")
        
        if not content.startswith(self.bot._get_prefix):
            print(f"Rejected message: {msg} due to missing prefix: {self.bot._get_prefix}")
            return

        if self.broadcaster:
            json:dict[str:Any] = msg.to_json()
            self.broadcaster.broadcast(content=json)
        return

    @twitchio.ext.commands.Component.listener()
    async def event_automatic_redemption_add(self, payload:ChannelPointsAutoRedeemAdd):
        print(f"Redemption: {payload}")
        return

    @twitchio.ext.commands.Component.listener()
    async def event_custom_redemption_add(self, payload:ChannelPointsRedemptionAdd):
        print(f"Custom redemption: {payload}")
        redeem_name:str = payload.reward.title
        username:str = payload.user.display_name
        redeem_text:str = payload.user_input

        if redeem_name == "Change my BotGor font":
            print(f"{username} is changing their font to: {redeem_text}")
            asyncio.create_task(Database.Database_API.add_user(User(name=username, font=redeem_text)))

        return