from fastapi import FastAPI
from pydantic import BaseModel

from Core.Message_Routing import router

botgor = FastAPI(title="BotGor:app")

class JoinRequest(BaseModel):
    port:int

@botgor.get("/health")
def health() -> dict[str, str]:
    return {"ok": "good"}

@botgor.post("/join")
async def join(req:JoinRequest) -> dict[str, int]:
    router.add_listener(req.port)
    return {"joined": req.port}
