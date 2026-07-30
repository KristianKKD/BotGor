import httpx
from lib.API_Msgs import JOIN_MSG

BASE_IP:str = "http://localhost"

async def post(msg:str, port:int, body:dict[str, str]={}, timeout:int=3, name:str="") -> dict[str, str]:
    url:str = f"{BASE_IP}:{str(port)}/{msg}"
    if msg is not JOIN_MSG:
        print(f"{name} Sending POST: {url} - {body}")

    response:dict[str, str] = {}
    async with httpx.AsyncClient() as client:
        try:
            resp:httpx.Response = await client.post(url=url, json=body, timeout=timeout)
            response:dict[str, str] = resp.json()
        except Exception as e:
            return {}

    # if response and not response.get('detail', ''):
    print(f"{url} got response: {response}")
    return response

async def get(msg:str, port:int, url_body:str="", timeout:int=1, name:str="") -> dict[str, str]:
    url:str = f"{BASE_IP}:{str(port)}/{msg}/{url_body}"
    print(f"{name} Sending GET: {url}")

    response:dict[str, str] = {}
    async with httpx.AsyncClient() as client:
        try:
            resp:httpx.Response = await client.get(url=url, timeout=timeout)
            response:dict[str, str] = resp.json()
        except Exception as e:
            return {}

    # if response and not response.get('detail', ''):
    print(f"{url} got response: {response}")
    return response