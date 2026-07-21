import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.Environment import find_port, load_environment
from lib.API_Msgs import NAME, MSG
from lib.Broadcaster import Broadcaster

from Games.Games_Game import Game
from Games.Games_API import Games_Service

# wordbomb
# create a random set of events (can be outside the "game")
# website to take an input for n players
# save the inputs into a hidden 'player' list
# STT to track the words said
# if we get a word from the hidden list
#   play tts message
#   trigger a random event

class Player:
    def __init__(self, player_name:str, phrases:dict[str, int]=None):
        self.name:str = player_name
        self.triggers:dict[str, str] = phrases if phrases else {}
        self.damage:int = 0
        return
    
class WordBomb(Game):
    def __init__(self, players:list[Player], broadcaster:Broadcaster):
        self.players:list[Player] = players
        self.broadcaster:Broadcaster = broadcaster
        return

    def game_event(self, player:Player, sentence:str):
        lower_sentence:str = sentence.lower().strip()

        total_damage:int = 0
        found_phrases:list[str] = []

        phrase:str
        damage:str # should be converted to int
        for phrase, damage in player.triggers.items():
            if phrase.strip() in lower_sentence:
                total_damage = total_damage + int(damage)
                found_phrases.append(phrase)
                print(f"{player.name} said {phrase} for {damage} damage! total:{player.damage}")
        
        if total_damage:
            player.damage = player.damage + total_damage
            # Play tts "player_name said phrase..."
            self.broadcaster.broadcast({MSG:f"{player.name} said {' and '.join(found_phrases)} for {total_damage} damage!"})

        return
    
    def incoming_message(self, msg:dict[str, str]):
        # msgs should be {'user':'sentence spoken'}
        player:Player
        for player in self.players:
            if player.name in msg:
                self.game_event(sentence=msg[player.name])
        return
    
    def setup_message(self, msg:dict[str, str]):
        # msg should be {'name':'player', 'word':'weight', 'word':'weight',...}
        if not msg or not NAME in msg:
            return
        
        found_name:str = msg.pop(NAME).lower()
        
        player:Player
        for player in self.players:
            if player.name.lower() == found_name:
                player.triggers = msg
                break
        return   

    def reset_game(self):
        self.stop_game()
        self.explosions = 0
        self.start_game()
        return
    

async def run_wordbomb(manual_input=False):
    load_environment()

    krabgor:Player = Player(player_name="KrabGor")
    alt_player:Player = Player(player_name="Player2")

    broadcaster:Broadcaster = Broadcaster(name="WORDBOMB")
    wordbomb:WordBomb = WordBomb(players=[krabgor, alt_player], broadcaster=broadcaster)
    service:Games_Service = Games_Service(game=wordbomb, sub_ports=[find_port("DISCORD")], broadcaster=broadcaster, ui_enabled=manual_input)

    while not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_wordbomb(manual_input=True))
    