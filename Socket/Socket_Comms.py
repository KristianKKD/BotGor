import json
from websockets.asyncio.server import serve, Server, ServerConnection
from websockets.asyncio.client import connect
import asyncio
from typing import Any

from lib.Broadcaster import Broadcaster

class Socket_Comms:
    def __init__(self, port:int, broadcaster:Broadcaster):
        self.sock:Server = None
        self.broadcaster:Broadcaster = broadcaster
        asyncio.ensure_future(self._create_rec_socket(port=port))
        return

    async def _create_rec_socket(self, port:int):
        self.sock = await serve(handler=self._rec_loop, host="localhost", port=port)
        asyncio.create_task(self.sock.server.serve_forever())
        return

    async def _rec_loop(self, websocket:ServerConnection):
        message:str | bytes
        for message in websocket:
            json_dict:dict[str, Any] = json.loads(message)
            self.broadcaster.broadcast(content=json_dict)
        return

    async def send(self, uri:str, payload:dict[str, Any]):
        async with connect(uri=uri) as websocket:
            json_data:str = json.dumps(payload)
            await websocket.send(json_data)
        return
