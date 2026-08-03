import os
import asyncio
import sys
from multiprocessing.synchronize import Event as EventType

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment
from lib.Broadcaster import Broadcaster
from Socket.Socket_API import Socket_Service, APP_NAME
from Socket.Socket_Comms import Socket_Comms

async def run_socket(exit_flag:EventType=None, manual_input:bool=False):
    load_environment()

    broadcaster:Broadcaster = Broadcaster(name=APP_NAME)
    comms:Socket_Comms = Socket_Comms(broadcaster=broadcaster)
    service:Socket_Service = Socket_Service(broadcaster=broadcaster, ui_enabled=manual_input)
    while not (exit_flag and exit_flag.is_set()) and not service.shutdown:
        await asyncio.sleep(5)
    return

###############################################
if __name__ == "__main__":
    asyncio.run(run_socket(manual_input=True))