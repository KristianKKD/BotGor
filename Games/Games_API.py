from lib.MicroService import MicroServiceBase
from lib.Service_UI import Simple_UI

from Games.Games_Game import Game

from lib.API_Msgs import SETUP_MSG
from lib.Broadcaster import Broadcaster

APP_NAME:str = "GAMES"

class Games_Service(MicroServiceBase, Simple_UI):
    def __init__(self, game:Game, sub_ports:list[int], broadcaster:Broadcaster, ui_enabled:bool):
        self.game:Game = game

        MicroServiceBase.__init__(self=self, name=APP_NAME, subscription_ports=sub_ports)
        if ui_enabled:
            Simple_UI.__init__(self=self)
        return
    
    def _register_api(self):
        MicroServiceBase._register_api(self=self)

        @self.app.post(f"/{SETUP_MSG}")
        async def setup_msg(msg:dict[str, str]) -> dict[str, str]:
            response:dict[str, str] = MicroServiceBase.handle_msg(self=self, msg=msg)
            game_response:dict[str, str] | None = self.game.setup_message(msg=msg)
            response = game_response if game_response else response
            return response
        return
    
    def handle_msg(self, msg:dict[str, str]) -> dict[str, str]:
        response:dict[str, str] = MicroServiceBase.handle_msg(self=self, msg=msg)
        game_response:dict[str, str] | None = self.game.incoming_message(msg=msg)
        response = game_response if game_response else response
        return response
    