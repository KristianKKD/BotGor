import httpx
import time
from lib.API_Msgs import JOIN

BASE_IP:str = "http://localhost"

async def post(msg:str, port:int, json:dict[str, str]={}, timeout:int=10, name="") -> str:
    url = f"{BASE_IP}:{str(port)}/{msg}"
    response:dict[str, str] = {}
    if msg is not JOIN:
        print(f"{name} Sending: {url} - {json} | time:{time.time()}")
    async with httpx.AsyncClient() as client:
        try:
            resp:httpx.Response = await client.post(url=url, json=json, timeout=timeout)
            response:dict[str, str] = resp.json()
        except Exception as e:
            return {}

    if response and not response.get('detail', ''):
        print(f"{url} got response: {response} | time:{time.time()}")
    return response
