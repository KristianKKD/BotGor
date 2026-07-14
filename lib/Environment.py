import os
from dotenv import load_dotenv

KEYS_PATH:str = "keys.env"
PORTS_PATH:str = "ports.env"

def load_environment():
    print("Loading env variables")
    load_dotenv(KEYS_PATH)
    load_dotenv(PORTS_PATH)
    return

def find_port(name:str, retry:bool = False) -> int:
    try:
        found:str = os.environ[name]
    except:
        if retry:
            raise ValueError(f"No port found for {name}")
        else:
            load_environment()
            return find_port(name=name, retry=True)
    return int(found)