import asyncio
import aioconsole

from typing import Awaitable

from lib.MicroService import MicroServiceBase

class Simple_UI():
    def __init__(self, commands:dict[str, Awaitable[bool]]=None):
        self.commands:dict[str, Awaitable[bool]] = (commands if commands else {}) | {'exit' : self.close_service}
        self._shutting_down_ui:bool = False

        self.display_ui_msg:bool = True # Display a msg every time we enter an input

        asyncio.ensure_future(self._input_loop())
        return
    
    def shutdown_ui(self):
        self._shutting_down_ui = True
        return

    async def _input_loop(self):
        while not self._shutting_down_ui:
            try:
                if self.display_ui_msg:
                    print("Enter input:")
                    self.display_ui_msg = False
                
                user_input:str = await aioconsole.ainput()
                if user_input:
                    print(f"Got: {user_input}")
                if self._shutting_down_ui or not await self.handle_input(user_input=user_input):
                    break
            except EOFError:
                break
        return

    async def handle_input(self, user_input:str):
        cmd:str = user_input.lower().strip()
        arg:str = ""

        if ':' in user_input:
            cmd, arg = user_input.split(':', 1)

        should_continue:bool = True

        if cmd:
            self.display_ui_msg = True

            if cmd in self.commands:
                should_continue = await self.commands[cmd](arg)
            else:
                print("Invalid input:" + user_input)

        return should_continue
    
    async def close_service(self, _:str) -> bool:
        self.shutdown_ui()
        if isinstance(self, MicroServiceBase):
            MicroServiceBase.service_shutdown(self)
        return False