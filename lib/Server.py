import uvicorn
import asyncio
import time

class Server():
    def __init__(self, app, port:int):
        async def launch_server():
            self.server = uvicorn.Server(self.config)
            await self.server.serve()

        self.config = uvicorn.Config(app=app, host="127.0.0.1", port=port, reload=False)
        asyncio.create_task(launch_server())
        return

    def close_server(self):
        while(self.server is None):
            print("Waiting for server to start so we can close it lmao")
            time.sleep(1)

        self.server.should_exit = True
        return
