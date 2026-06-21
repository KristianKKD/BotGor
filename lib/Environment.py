
from dotenv import load_dotenv
import os

def load_environment():
    KEYS_PATH:str = "keys.env"
    PORTS_PATH:str = "ports.env"

    print("Loading env variables")
    load_dotenv(KEYS_PATH)
    if not os.environ["TWITCH_TOKEN"] or not os.environ["TWITCH_CLIENT_ID"]:
        raise ValueError("TWITCH_TOKEN and TWITCH_CLIENT_ID must be set in the environment variables.")
    
    load_dotenv(PORTS_PATH)
    return

def find_port(name:str, retry:bool = False) -> int:
    found:str = os.environ[name]
    if not found:
        if retry:
            raise ValueError(f"No port found for {name}")
        else:
            load_environment()
    return int(found)