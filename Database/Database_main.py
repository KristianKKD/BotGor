import os
import sys
import asyncio
from multiprocessing.synchronize import Event as EventType

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment

from Database.Database_Manager import Database_UserManager
from Database.Database_API import Database_Service

async def run_database(exit_flag:EventType=None, manual_input:bool=False):
    load_environment()

    manager:Database_UserManager = Database_UserManager()
    service:Database_Service = Database_Service(manager=manager, ui_enabled=manual_input)

    while not (exit_flag and exit_flag.is_set()) and not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_database(manual_input=True))
    