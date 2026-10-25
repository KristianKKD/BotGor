import os
import asyncio
import sys
import base64
import hashlib
from multiprocessing.synchronize import Event as EventType
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import load_environment
from lib.Broadcaster import Broadcaster
from Socket.Socket_API import Socket_Service, APP_NAME
from Socket.Socket_Comms import Socket_Comms

async def run_socket(exit_flag:EventType=None, manual_input:bool=False):
    load_environment()

    broadcaster:Broadcaster = Broadcaster(name=APP_NAME)
    await connect_to_obs(broadcaster=broadcaster, manual_input=manual_input, exit_flag=exit_flag)
    return

async def connect_to_obs(broadcaster:Broadcaster, manual_input:bool, exit_flag:EventType):
    def obs_auth_string(password:str, salt:str, challenge:str) -> str:
        secret:str = base64.b64encode(
            hashlib.sha256((password + salt).encode("utf-8")).digest()
        ).decode("utf-8")

        return base64.b64encode(
            hashlib.sha256((secret + challenge).encode("utf-8")).digest()
        ).decode("utf-8")

    comms:Socket_Comms = Socket_Comms(broadcaster=broadcaster)
    service:Socket_Service = Socket_Service(comms=comms, broadcaster=broadcaster, ui_enabled=manual_input)

    obs_auth:dict[str, Any] | None = await comms.open(uri="ws://localhost:4455", port=4455)
    if not auth_response:
        raise ConnectionRefusedError("Failed to connect to OBS")

    auth_info:dict[str, Any] | None = obs_auth.get("d", {}).get("authentication", None)
    if not auth_info:
        raise ValueError("Failed to get authentication details from OBS")
    
    auth_salt:str | None = auth_info.get("salt", None)
    auth_challenge:str | None = auth_info.get("challenge", None)
    if not auth_salt or not auth_challenge:
        raise ValueError("Failed to find challenge+salt in authentication from OBS")

    authentication_string:str = obs_auth_string(password=os.environ["OBS_WEBSOCKET_PASSWORD"],
                                                salt=auth_salt,
                                                challenge=auth_challenge
                                                )

    authentication:dict[str, Any] = {
        "op":1,
        "d":{
            "rpcVersion":1,
            "authentication":authentication_string
        }
    }
    auth_response:dict[str, Any] = await comms.send_rec(authentication)
    if auth_response.get("op", None) != 2:
        raise ValueError(f"OBS returned a failure code for authentication: {auth_response}")
    

    while not (exit_flag and exit_flag.is_set()) and not service.shutdown:
        await asyncio.sleep(5)
    return



###############################################
if __name__ == "__main__":
    asyncio.run(run_socket(manual_input=True))