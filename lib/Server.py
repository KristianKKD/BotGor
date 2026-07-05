import uvicorn
import threading
import asyncio
import time

class Server:
    def __init__(self, app, port: int):
        self.config = uvicorn.Config(app=app, host="127.0.0.1", port=port, reload=False)
        self.server = None
        self._ready = threading.Event()

        thread = threading.Thread(target=self._run_server, daemon=True)
        thread.start()

        self._ready.wait()

    def _run_server(self):
        self.server = uvicorn.Server(self.config)

        original_startup = self.server.startup

        async def patched_startup(sockets=None):
            await original_startup(sockets)
            self._ready.set()

        self.server.startup = patched_startup
        asyncio.run(self.server.serve())

    def close_server(self):
        self._ready.wait()
        self.server.should_exit = True