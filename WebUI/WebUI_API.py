from typing import Awaitable
from pathlib import Path

from lib.MicroService import MicroServiceBase
from lib.Service_UI import Simple_UI
from lib.TwitchMsg import split_message

from django.http import HttpResponse
from django.urls import path

APP_NAME:str = "WEBUI"
INDEX_PAGE_PATH:Path = Path(__file__).with_name("Pages/index.html")

def index(request):
    page:str = INDEX_PAGE_PATH.read_text(encoding="utf-8")
    return HttpResponse(page, content_type="text/html; charset=utf-8")

def latest_text(request):
    text:str = WebUI_Service.latest_shown_text
    return HttpResponse(content=text, content_type="text/plain; charset=utf-8")

urlpatterns = [
    path("", index),
    path("text", latest_text),
]

class WebUI_Service(MicroServiceBase, Simple_UI):
    def __init__(self, subscription_ports:list[int], ui_enabled:bool):
        WebUI_Service.latest_shown_text = ""

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
        if content:
            WebUI_Service.latest_shown_text = content

        return response

    async def display_text(self, text:str) -> bool:
        WebUI_Service.latest_shown_text = text
        return True
