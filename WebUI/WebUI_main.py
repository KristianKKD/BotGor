import os
import sys
import asyncio
from multiprocessing.synchronize import Event as EventType

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
from django.core.asgi import get_asgi_application

from lib.Environment import load_environment, find_port
from WebUI.WebUI_API import WebUI_Service

async def run_webui(exit_flag:EventType=None, manual_input:bool=False):
    load_environment()
    
    django.conf.settings.configure(SECRET_KEY=os.environ["DJANGO_SECRET_KEY"], DEBUG=True, ROOT_URLCONF="WebUI.WebUI_views")
    django.setup()

    service:WebUI_Service = WebUI_Service(subscription_ports=[find_port("TWITCH"), find_port("DISCORD"), find_port("CHATBOT")], ui_enabled=manual_input)
    service.app.mount("/", get_asgi_application()) # Mount the Django port to the FastAPI port

    while not (exit_flag and exit_flag.is_set()) and not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_webui(manual_input=True))
