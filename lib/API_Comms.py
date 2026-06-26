import httpx

from lib.Environment import find_port

BASE_IP:str = "http://127.0.0.1"

def join_listeners(port:int) -> str:
    join_msg:str = "join"
    botgor_port:int = find_port("TWITCH")
    return post(msg=f"{join_msg}", data=str(port), port=botgor_port)

def post(msg:str, data:str, port:int) -> str:
    url = f"{BASE_IP}:{str(port)}"
    response:dict[str, str] = {}
    try:
        response = httpx.post(f"{url}/{msg}", data=data, timeout=2).json()
    except:
        pass

    return response
