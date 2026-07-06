import httpx

BASE_IP:str = "http://localhost"

async def post(msg:str, port:int, json:dict[str, str]={}, timeout:int=5) -> str:
    url = f"{BASE_IP}:{str(port)}/{msg}"
    response:dict[str, str] = {}
    #print(f"Sending: {url} - {json}")
    async with httpx.AsyncClient() as client:
        try:
            resp:httpx.Response = await client.post(url=url, json=json, timeout=timeout)
            response:dict[str, str] = resp.json()
        except Exception as e:
            pass

    if response:
        print(f"{url} got response: {response}")
    return response
