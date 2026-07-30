from typing import Awaitable
from pathlib import Path
import asyncio

from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import path

from lib.MicroService import MicroServiceBase
from lib.API_Msgs import SIZE_KEY, FONT_KEY, RESPONSE_KEY, NAME_KEY, CONTENT_KEY
import Database.Database_API
from Database.Database_User import User


APP_NAME:str = "WEBUI"
INDEX_PAGE_PATH:Path = (Path(__file__).parent / "Pages" / "index.html")

def index(request):
    page:str = INDEX_PAGE_PATH.read_text(encoding="utf-8")
    return HttpResponse(page, content_type="text/html; charset=utf-8")

def latest_text(request):
    text:str = '\n'.join([font.text for font in WebUI_Service.shown_text])
    return HttpResponse(content=text, content_type="text/plain; charset=utf-8")

def latest_text_lines(request):
    lines:list[dict[str, str | int]] = [
        {
            "text": font.text,
            "font": font.font_name,
            "size": font.size,
        }
        for font in WebUI_Service.shown_text
    ]
    return JsonResponse({"lines": lines})

urlpatterns = [
    path("", index),
    path("text", latest_text),
    path("text/lines", latest_text_lines),
]

class Font:
    def __init__(self, text:str, size:int=24, font_name:str="arial"):
        self.text:str = text
        self.size:int = int(size) if size else 24
        self.font_name:str = font_name if font_name else "arial"
        return

    def __str__(self):
        return self.text

class WebUI_Service(MicroServiceBase):
    def __init__(self, subscription_ports:list[int], ui_enabled:bool):
        WebUI_Service.shown_text:list[Font] = []

        commands:dict[str, Awaitable] = {"text":self.display_text}

        MicroServiceBase.__init__(self=self, name=APP_NAME, subscription_ports=subscription_ports, ui_enabled=ui_enabled, commands=commands)
        return

    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        async def display_text(username:str, content:str):
            user_data:User = await Database.Database_API.get_user(username=username)
            font_name:str = user_data.get(key=FONT_KEY)
            font_size:str = user_data.get(key=SIZE_KEY, expected_type=int)

            self.add_text(self.create_font(text=f"{username}: {content}", size=font_size, font_name=font_name))
            return
        
        response:dict[str, str] = await MicroServiceBase.handle_msg(self=self, msg=msg)

        name:str = msg.get(NAME_KEY, "")
        content:str = msg.get(CONTENT_KEY, msg.get(RESPONSE_KEY, ""))

        if content:
            asyncio.create_task(display_text(username=name, content=content))

        return response

    def create_font(self, text:str, size:int=None, font_name:str=None) -> Font:
        return Font(text=text, size=size, font_name=font_name)

    def add_text(self, font:Font):
        MAX_LINES_SHOWN:int = 20
        while(len(self.shown_text) >= MAX_LINES_SHOWN):
            self.shown_text.pop(0)
        WebUI_Service.shown_text.append(font)
        return

    async def display_text(self, text:str) -> bool:
        self.add_text(self.create_font(text=text, font_name=""))
        return True
