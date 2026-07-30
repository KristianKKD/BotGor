import json
from typing import Any
from lib.API_Msgs import NAME_KEY, CONTENT_KEY
from Database.Database_Setting import Settings, TwitchSettings

class User:
    def __init__(self, name:str="", settings:list[Settings]=None, data:dict[str, str]=None):
        self.name:str = name

        if settings and not isinstance(settings, list):
            settings = [settings]
        self.settings = settings if settings else []

        if data:
            self._load_data(data=data)

        if not self.name:
            raise ValueError("Must provide name or data to user!")
        return

    def _load_data(self, data:dict[str, str]):
        self.name = data.get(NAME_KEY, "")

        # Convert the data from CONTENT: {data} to just {data}
        try:
            content = json.loads(data[CONTENT_KEY].replace("'", '"'))
            data.update(content)
        except:
            pass

        known_setting_class:list[Settings] = [TwitchSettings] # List of classes that inherit from Setting

        # Re-construct an object from json data based on known setting types
        setting_class:Settings
        for setting_class in known_setting_class:
            setting:Settings = setting_class.from_json(data)
            if setting:
                self.settings.append(setting)

        return

    def get(self, key:str, expected_type:type=None) -> Any | None:
        data:dict[str, Any] = self.to_json()
        value:Any | None = data.get(key, None)
        if expected_type:
            old_type:type = type(value)
            try:
                value = expected_type(value)
            except:
                print(f"Failed to convert {key}:{value} to {str(expected_type)} from {str(old_type)}")
                value = None
        return value

    def to_json(self) -> dict[str, str]:
        data:dict[str, Any] = {NAME_KEY: self.name}
        for setting in self.settings:
            data.update(setting.to_json())  # merge each setting dict
        return data
    
    def __str__(self) -> str:
        return str(self.to_json())