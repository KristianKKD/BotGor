from typing import Any
from Database.Database_User import User
from Database.Database_Setting import Settings
from dataclasses import asdict

class Database_UserManager:
    def __init__(self):
        self._users: dict[str, User] = {}
        return

    def get_user(self, name:str) -> User | None:
        user:User | Any = self._users.get(name, None)
        print(f"Found user: {str(user) if user else 'NOT FOUND'}")
        return user if user else None
    
    def add_user(self, new_user:User) -> User:
        if new_user.name not in self._users:
            self._users[new_user.name] = new_user
        else:
            old_user:User = self._users[new_user.name]

            new_setting:Settings
            for new_setting in new_user.settings:
                old_setting:Settings = next((setting for setting in old_user.settings 
                                           if type(setting) == type(new_setting)), None)

                if old_setting: # If we already have that kind of settings, modify
                    for attr, value in asdict(new_setting).items():
                        if value:
                            setattr(old_setting, attr, value)

                else: # Incoming new settings
                    old_user.settings.append(new_setting)
        return new_user

    def remove_user(self, name:str) -> User | None:
        print(f"Removing {name}")
        return self._users.pop(name, None)

    def find_all_users(self) -> list[User]:
        return list(self._users.values())