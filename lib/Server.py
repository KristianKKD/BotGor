import uvicorn
import threading
import asyncio
import time

class Server:
    def __init__(self, app, port:int):
        self.config = uvicorn.Config(app=app, host="127.0.0.1", port=port, reload=False)
        self.server = None
        _ready = threading.Event()

        thread = threading.Thread(target=self._run_server, args=(_ready,), daemon=True)
        thread.start()

        _ready.wait()
        return

    def _run_server(self, ready_flag):
        self.server = uvicorn.Server(self.config)
        ready_flag.set()
        asyncio.run(self.server.serve())
        return

    def close_server(self):
        while(self.server is None):
            print("Waiting for server to start so we can close it lmao")
            time.sleep(1)

        self.server.should_exit = True
        return

