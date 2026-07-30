import asyncio
import aioconsole

from typing import Awaitable

class Simple_UI():
    def __init__(self, 
                 ui_enabled:bool = False,
                 commands:dict[str, Awaitable[bool]] = None,
                 ui_name:str="",
                 ):

        DEFAULT_COMMANDS:dict[str, Awaitable[bool]] = {'exit':self.close_service, 'help':self.help}
        self.commands:dict[str, Awaitable[bool]] = (commands if commands else {}) | DEFAULT_COMMANDS
        self.shutting_down_ui:bool = False

        self.display_ui_msg:bool = True # Display a msg every time we enter an input
        self.ui_name:str = ui_name

        if ui_enabled:
            asyncio.ensure_future(self._input_loop())
        return
    
    def shutdown_ui(self):
        self.shutting_down_ui = True
        return

    async def _input_loop(self):
        while not self.shutting_down_ui:
            try:
                if self.display_ui_msg:
                    print(f"{self.ui_name}: Enter input:")
                    self.display_ui_msg = False
                
                user_input:str = await aioconsole.ainput()
                if user_input:
                    print(f"{self.ui_name}: Got {user_input}")
                if self.shutting_down_ui or not await self.handle_input(user_input=user_input):
                    print(f"{self.ui_name}: Shutting down UI...")
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
        self.display_ui_msg = True

        if cmd in self.commands:
            should_continue = await self.commands[cmd](arg)
        else:
            print(f"{self.ui_name}: Got invalid input: {user_input}")

        return should_continue
    
    async def close_service(self, _:str) -> bool:
        # Lazy import to avoid circular dependency
        from lib.MicroService import MicroServiceBase
        
        self.shutdown_ui()
        if isinstance(self, MicroServiceBase):
            MicroServiceBase.service_shutdown(self)
        return False

    async def help(self, _:str) -> bool:
        print(f"Commands for {self.ui_name} are: {', '.join(self.commands.keys())}")
        return True