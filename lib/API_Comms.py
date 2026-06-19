import httpx

async def join_listeners(port:int):
    join_msg:str = "join"
    post(f"{join_msg}/{port}")
    return

async def post(content:str, port:int) -> str:
    base = f"http://127.0.0.1:{port}"

    reply = await httpx.post(f"{base}/{content}", timeout=2).json()

    return reply
