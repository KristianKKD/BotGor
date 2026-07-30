from typing import Any
from Database.Database_User import User

class Database_UserManager:
    def __init__(self):
        self._users: dict[str, User] = {}
        return

    def get_user(self, name:str) -> User | None:
        user:User | Any = self._users.get(name, None)
        print(f"Found user: {str(user) if user else 'NOT FOUND'}")
        return user if user else None
    
    def add_user(self, new_user:User):
        if not new_user.name in self._users:
            print(f"Adding {str(new_user)}")
            self._users[new_user.name] = new_user
        else:
            old_user:User = self._users[new_user.name]
            print(f"Modifying {str(old_user)} to {str(new_user)}")
            for attr, value in vars(new_user).items():
                if value:
                    setattr(old_user, attr, value)
        return

    def remove_user(self, name:str) -> User | None:
        print(f"Removing {name}")
        return self._users.pop(name, None)

    def find_all_users(self) -> list[User]:
        return list(self._users.values())