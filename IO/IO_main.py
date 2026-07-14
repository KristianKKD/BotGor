import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment

from IO.IO_Handler import IO_Handler
from IO.IO_API import IO_Service

async def run_io(manual_input=False):
    load_environment()

    io:IO_Handler = IO_Handler()
    service:IO_Service = IO_Service(io_handler=io, ui_enabled=manual_input)

    while not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_io(manual_input=True))
    