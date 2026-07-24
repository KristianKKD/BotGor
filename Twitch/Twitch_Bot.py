import os
import asyncio

import twitchio
from twitchio.ext.commands import Bot, AutoBot, CommandErrorPayload
from twitchio.ext.commands.exceptions import CommandNotFound
from twitchio import eventsub, ChatMessage, WebsocketWelcome, authentication, TokenRefreshedPayload, SubscriptionRevoked, ChannelPointsAutoRedeemAdd, ChannelPointsRedemptionAdd

from lib.TwitchMsg import TwitchMsg
from lib.Broadcaster import Broadcaster

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

    async def event_token_refreshed(self, payload:TokenRefreshedPayload):
        print(f"[TWITCH AUTH] Token refreshed for user_id={payload.user_id} expires_in={payload.expires_in}s")
        return

    async def event_subscription_revoked(self, payload:SubscriptionRevoked):
        print(f"[TWITCH AUTH WARNING] Subscription revoked")
        return

    async def event_error(self, payload:twitchio.EventErrorPayload):
        print(
            f"[TWITCH EVENT ERROR] listener={payload.listener.__name__} "
            f"error={payload.error!r}"
        )
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
        
        msg:TwitchMsg = TwitchMsg(user=user, content=content)
        print(f"Message created: {msg}")
        
        if not content.startswith(self.bot._get_prefix):
            print(f"Rejected message: {msg} due to missing prefix: {self.bot._get_prefix}")
            return

        if self.broadcaster:
            self.broadcaster.broadcast(content=msg.to_json())
        return

    @twitchio.ext.commands.Component.listener()
    async def event_automatic_redemption_add(self, payload:ChannelPointsAutoRedeemAdd):
        print(f"Redemption: {payload}")
        return

    @twitchio.ext.commands.Component.listener()
    async def event_custom_redemption_add(self, payload:ChannelPointsRedemptionAdd):
        print(f"Custom redemption: {payload}")
        return