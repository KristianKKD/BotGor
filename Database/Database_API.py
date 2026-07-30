from typing import Awaitable

from lib.MicroService import MicroServiceBase
from lib.API_Msgs import NAME_KEY, CONTENT_KEY, ERROR_VALUE
from lib.Environment import find_port
from lib.API_REST import get, post

from Database.Database_Manager import Database_UserManager
from Database.Database_User import User


APP_NAME:str = "DATABASE"

class Database_Service(MicroServiceBase):
    def __init__(self, manager:Database_UserManager, ui_enabled:bool):
        self.manager:Database_UserManager = manager

        commands:dict[str, Awaitable] = {"add":self.add_user_manual, "show":self.show_all_users}
        MicroServiceBase.__init__(self=self, name=APP_NAME, ui_enabled=ui_enabled, commands=commands)
        return

    def _register_api(self):
        MicroServiceBase._register_api(self=self)

        @self.app.get(f"/{NAME_KEY}/" + "{name}")
        async def get_user(name:str) -> dict[str, str]:
            user:str = self.manager.get_user(name=name)
            response:dict[str, str] = {NAME_KEY:name, CONTENT_KEY:str(user) if user else ERROR_VALUE}
            return response
        
        @self.app.post(f"/{NAME_KEY}")
        async def add_user(msg:dict[str, str]) -> dict[str, str]:
            user:User = User(data=msg)
            self.manager.add_user(new_user=user)
            return {NAME_KEY:user.name, CONTENT_KEY:str(user.to_json())}
        
        return

    async def add_user_manual(self, name:str) -> bool:
        self.manager.add_user(User(name=name))
        return True

    async def show_all_users(self, _) -> bool:
        for user in self.manager.find_all_users():
            print(user)
        return True


async def get_user(username:str) -> User | None:
    user_data:dict[str, str] = await get(msg=NAME_KEY, port=find_port(name=APP_NAME), url_body=username)
    content:str | dict[str, str] = user_data.get(CONTENT_KEY, ERROR_VALUE)
    return User(data=user_data) if content and content != ERROR_VALUE else None

async def add_user(user:User) -> dict[str, str]:
    response:dict[str ,str] = await post(msg=NAME_KEY, port=find_port(name=APP_NAME), body=user.to_json())
    return response