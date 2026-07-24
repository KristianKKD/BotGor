from typing import Awaitable
from pathlib import Path

from lib.MicroService import MicroServiceBase
from lib.Service_UI import Simple_UI
from lib.TwitchMsg import split_message
from lib.API_Msgs import SIZE_MSG, FONT_MSG

from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import path

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

class WebUI_Service(MicroServiceBase, Simple_UI):
    def __init__(self, subscription_ports:list[int], ui_enabled:bool):
        WebUI_Service.shown_text:list[Font] = []

        commands:dict[str, Awaitable] = {"text":self.display_text}

        MicroServiceBase.__init__(self=self, name=APP_NAME, subscription_ports=subscription_ports)
        if ui_enabled:
            Simple_UI.__init__(self=self, commands=commands)
        return

    async def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        response:dict[str, str] = await MicroServiceBase.handle_msg(self=self, msg=msg)

        user:str
        content:str
        user, content = split_message(msg=msg)

        size:str = msg.get(SIZE_MSG, None)
        font_name:str = msg.get(FONT_MSG, None)

        if content:
            self.add_text(self.create_font(text=content, size=size, font_name=font_name))
            WebUI_Service.latest_shown_text = content

        return response

    def create_font(self, text:str, size:int=None, font_name:str=None) -> Font:
        return Font(text=text, size=size, font_name=font_name)

    def add_text(self, font:Font):
        WebUI_Service.shown_text.append(font)
        return

    async def display_text(self, text:str) -> bool:
        self.add_text(self.create_font(text=text))
        return True
