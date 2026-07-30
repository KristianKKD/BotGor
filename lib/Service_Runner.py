import asyncio
from typing import Awaitable, Callable
from multiprocessing import Process, Event
from multiprocessing.synchronize import Event as EventType
from collections import defaultdict

from lib.Service_UI import Simple_UI
from lib.API_REST import post
from lib.API_Msgs import COMMAND_MSG, CONTENT_KEY, SHUTDOWN_MSG
from lib.Environment import find_port

def _run_async_in_process(async_func:Callable, *args):
    asyncio.run(async_func(*args))
    return

class ServiceRunner(Simple_UI):
    def __init__(self, all_mains:dict[str, Awaitable], start_mains:dict[str, Awaitable]):
        self.processes:dict[str, Process] = defaultdict(Process)
        self.exit_flag:EventType = Event()

        self.all_mains:dict[str, Awaitable] = all_mains

        # Start all services concurrently in a single event loop
        if start_mains:
            asyncio.ensure_future(self._start_all_services(start_mains))

        commands:dict[str, Awaitable] = {'`':self.send_command,
                                         'shutdown':self.shutdown_service,
                                         'restart':self.restart_service,
                                         'start':self.start_service,
                                         'services':self.list_services,
                                         }
        Simple_UI.__init__(self=self, ui_enabled=True, commands=commands, ui_name="Runner")
        return
    
    async def _start_all_services(self, service_names:dict[str, Awaitable]):
        await asyncio.gather(*[self.start_service(process_name=name) for name in service_names])
        return

    def signal_exit(self):
        self.exit_flag.set()
        return

    def __del__(self):
        self.signal_exit()
        for p in self.processes:
            p.join()
        return

    async def send_command(self, content:str) -> bool:
        target, user_input = content.split(':', 1)
        
        # Where there's no argument
        if ':' in user_input:
            cmd, arg = user_input.split(':', 1)
        else:
            cmd = user_input
            arg = ''

        port:int = 0
        try:
            port = find_port(target.upper())
        except ValueError:
            print("Incorrect port")
            return True
            
        await post(msg=COMMAND_MSG, port=port, body={COMMAND_MSG:cmd, CONTENT_KEY:arg})
        return True

    async def shutdown_service(self, process_name:str) -> bool:
        if process_name in self.processes:
            print(f"Shutting down {process_name}")
            await post(msg=SHUTDOWN_MSG, port=find_port(process_name))
            p:Process = self.processes.pop(process_name)
            print("Waiting for process to shut down...")
            p.join()
        else:
            print(f"Couldn't find active process with the name: {process_name}")
        return True

    async def restart_service(self, process_name:str) -> bool:
        print(f"Restarting {process_name} service...")
        await self.shutdown_service(process_name=process_name)
        await self.start_service(process_name=process_name)
        return True

    async def start_service(self, process_name:str) -> bool:
        print(f"Launching {process_name}...")
        p:Process = Process(target=_run_async_in_process, args=(self.all_mains[process_name], self.exit_flag))
        p.start()
        self.processes[process_name] = p
        return True

    async def list_services(self, _:str) -> bool:
        active:list[str] = [name for name in self.processes]
        inactive:list[str] = [name for name in self.processes if not name in self.processes]
        print(f"Active: {active}\nInactive: {inactive}")
        return True