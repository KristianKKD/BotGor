import json
import asyncio
from asyncio import Future, Lock, Queue
from websockets.asyncio.client import ClientConnection, connect
from typing import Any, AsyncGenerator
from uuid import uuid4, UUID

from lib.Broadcaster import Broadcaster

class Socket_Comms:
    def __init__(self, broadcaster:Broadcaster):
        self.websocket:ClientConnection | None = None

        self.rec_loop:asyncio.Task[None] | None = None
        self.send_lock:Lock = Lock()

        self.pending:dict[str, Future[dict[str, Any]]] = {}
        self.incoming:Queue[dict[str, Any]] = Queue()

        self.broadcaster:Broadcaster = broadcaster
        return

    async def open(self, uri:str, port:int, auth_timeout:int=5) -> dict[str, Any] | None:
        self.websocket = await connect(uri=uri, port=port)
        self.rec_loop = asyncio.create_task(self._rec_loop(websocket=self.websocket))

        if auth_timeout <= 0:
            return None
        
        return await asyncio.wait_for(self.incoming.get(), timeout=auth_timeout) # If an auth message comes in, return it

    async def _rec_loop(self, websocket:ClientConnection) -> None:
        msg:str | bytes
        async for msg in websocket:
            data:dict[str, Any] = json.loads(s=msg)

            request_id:int | None = data.get("id", None)
            future:Future | None = self.pending.get(request_id, None)

            if future is not None and not future.done():
                future.set_result(data)
            else: # Message that we aren't necessarily waiting for
                print(f"Received {data}")
                self.incoming.put_nowait(data)
                self.broadcaster.broadcast(content=data)
        return

    async def send(self, payload:dict[str, Any]):
        if self.websocket is None:
            raise RuntimeError("WebSocket is not connected")

        async with self.send_lock:
            data:str = json.dumps(obj=payload)
            await self.websocket.send(message=data)
        return

    async def send_rec(self, payload:dict[str, Any], timeout:float=10) -> dict[str, Any]:
        request_id:UUID = str(uuid4())
        message:dict[str, Any] = {"id":request_id, **payload}

        future:Future = asyncio.get_running_loop().create_future()
        self.pending[request_id] = future

        try:
            await self.send(message)
            response:dict[str, Any] = await asyncio.wait_for(future, timeout=timeout)
        finally:
            self.pending.pop(request_id, None)

        return response

    async def close(self):
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

        if self.rec_loop is not None:
            await self.reader_task
            self.reader_task = None