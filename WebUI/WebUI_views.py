from pathlib import Path
import asyncio
import json
import subprocess
import sys

from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from lib.API_Msgs import HEARTBEAT_MSG, SHUTDOWN_MSG
from lib.API_REST import post
from lib.Environment import find_port

INDEX_PAGE_PATH:Path = (Path(__file__).parent / "Pages" / "index.html")
SERVICES_PAGE_PATH:Path = (Path(__file__).parent / "Pages" / "services.html")

# Service definitions: name -> main file path
PROJECT_ROOT:Path = Path(__file__).parent.parent
SERVICES:dict[str, Path] = {
    "TWITCH": PROJECT_ROOT / "Twitch" / "Twitch_main.py",
    "DISCORD": PROJECT_ROOT / "Discord" / "Discord_main.py",
    "CHATBOT": PROJECT_ROOT / "Chatbot" / "Chatbot_main.py",
    "TTS": PROJECT_ROOT / "TTS" / "TTS_main.py",
    "IO": PROJECT_ROOT / "IO" / "IO_main.py",
    "DATABASE": PROJECT_ROOT / "Database" / "Database_main.py",
    "GAMES": PROJECT_ROOT / "Games" / "Games_WordBomb_main.py",
}

APP_NAME:str = "WEBUI"

def index(request):
    page:str = INDEX_PAGE_PATH.read_text(encoding="utf-8")
    return HttpResponse(page, content_type="text/html; charset=utf-8")

def services_page(request):
    page:str = SERVICES_PAGE_PATH.read_text(encoding="utf-8")
    return HttpResponse(page, content_type="text/html; charset=utf-8")

def latest_text_lines(request):
    from WebUI.WebUI_API import WebUI_Service
    
    lines:list[dict[str, str | int]] = [
        {
            "text": font.text,
            "font": font.font_name,
            "size": font.size,
        }
        for font in WebUI_Service.shown_text
    ]
    return JsonResponse({"lines": lines})

def services_list(request):
    """Check which services are active by sending heartbeat requests"""
    async def check_service_status():
        services_status = {}
        
        for service_name in SERVICES.keys():
            try:
                port = find_port(service_name)
                response = await post(
                    msg=HEARTBEAT_MSG,
                    port=port,
                    body={HEARTBEAT_MSG: APP_NAME},
                    timeout=1,
                    name=APP_NAME
                )
                # If we get a response, service is active
                services_status[service_name] = "active" if response else "inactive"
            except Exception:
                services_status[service_name] = "inactive"
        
        return services_status
    
    # Run async check synchronously
    services_status = asyncio.run(check_service_status())
    return JsonResponse({"services": services_status})

@csrf_exempt
def service_start(request):
    """Start a service by launching its main file as a subprocess"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        service_name = data.get('service', '').upper()
        
        if not service_name:
            return JsonResponse({"error": "Service name required"}, status=400)
        
        if service_name not in SERVICES:
            return JsonResponse({"error": f"Unknown service: {service_name}"}, status=404)
        
        main_file = SERVICES[service_name]
        if not main_file.exists():
            return JsonResponse({"error": f"Service main file not found: {main_file}"}, status=404)
        
        # Start the service as a subprocess
        subprocess.Popen(
            [sys.executable, str(main_file)],
            cwd=str(PROJECT_ROOT),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        return JsonResponse({"status": "ok", "action": "start", "service": service_name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def service_stop(request):
    """Stop a service by sending it a shutdown command"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    async def stop_service_async(service_name: str):
        try:
            port = find_port(service_name)
            await post(
                msg=SHUTDOWN_MSG,
                port=port,
                body={SHUTDOWN_MSG: APP_NAME},
                timeout=3,
                name=APP_NAME
            )
            return True
        except Exception as e:
            print(f"Error stopping {service_name}: {e}")
            return False
    
    try:
        data = json.loads(request.body)
        service_name = data.get('service', '').upper()
        
        if not service_name:
            return JsonResponse({"error": "Service name required"}, status=400)
        
        if service_name not in SERVICES:
            return JsonResponse({"error": f"Unknown service: {service_name}"}, status=404)
        
        # Send shutdown command synchronously
        success = asyncio.run(stop_service_async(service_name))
        
        return JsonResponse({"status": "ok", "action": "stop", "service": service_name, "success": success})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def service_restart(request):
    """Restart a service by stopping then starting it"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    async def restart_service_async(service_name: str):
        try:
            # Stop the service
            port = find_port(service_name)
            await post(
                msg=SHUTDOWN_MSG,
                port=port,
                body={SHUTDOWN_MSG: APP_NAME},
                timeout=3,
                name=APP_NAME
            )
            
            # Wait a bit for shutdown
            await asyncio.sleep(2)
            
            # Start the service
            main_file = SERVICES[service_name]
            subprocess.Popen(
                [sys.executable, str(main_file)],
                cwd=str(PROJECT_ROOT),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            return True
        except Exception as e:
            print(f"Error restarting {service_name}: {e}")
            return False
    
    try:
        data = json.loads(request.body)
        service_name = data.get('service', '').upper()
        
        if not service_name:
            return JsonResponse({"error": "Service name required"}, status=400)
        
        if service_name not in SERVICES:
            return JsonResponse({"error": f"Unknown service: {service_name}"}, status=404)
        
        # Restart synchronously
        success = asyncio.run(restart_service_async(service_name))
        
        return JsonResponse({"status": "ok", "action": "restart", "service": service_name, "success": success})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

urlpatterns = [
    path("", index),
    path("services", services_page),
    path("text/lines", latest_text_lines),
    path("services/list", services_list),
    path("services/start", service_start),
    path("services/stop", service_stop),
    path("services/restart", service_restart),
]
