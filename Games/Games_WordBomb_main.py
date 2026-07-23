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
        self.seen_triggers:set[str] = {}
        self.damage:int = 0
        return
    
class WordBomb(Game):
    def __init__(self, players:list[Player], repeatable_triggers:bool, broadcaster:Broadcaster):
        self.players:list[Player] = players
        self.broadcaster:Broadcaster = broadcaster
        self.repeatable_triggers:bool = repeatable_triggers
        return

    def game_event(self, player:Player, sentence:str):
        lower_sentence:str = sentence.lower().strip()

        found_damage:list[str | int] = []
        found_phrases:list[str] = []

        int_damage:bool = False # Find out if we want to convert the damage

        phrase:str
        damage:str # Comes as str, should be converted to int
        for phrase, damage in player.triggers.items():
            if phrase.strip() in lower_sentence:
                
                # Check for 'seen' if enabled
                if not self.repeatable_triggers and phrase in player.seen_triggers:
                    continue
                player.seen_triggers.add(phrase)

                # Convert damage type
                try:
                    damage = int(damage)
                    int_damage = True
                except: # Damage may not be an int, could be a word
                    pass
                
                # Save
                found_damage.append(damage)
                found_phrases.append(phrase)
                print(f"{player.name} said {phrase} for {damage}!")
        
        if found_damage:
            output_phrases:str = ' and '.join(found_phrases)
            output_damage:str = ' '.join(found_damage)

            if int_damage:
                total_damage:int = sum(found_damage)
                output_damage = str(total_damage)
                player.damage = player.damage + total_damage

            # Play tts "player_name said phrase..."
            self.broadcaster.broadcast({MSG:f"{player.name} said {output_phrases} for {output_damage}!"})

        return
    
    def incoming_message(self, msg:dict[str, str]):
        # Msgs should be {'user':'sentence spoken'}
        player:Player
        for player in self.players:
            if player.name in msg:
                self.game_event(sentence=msg[player.name])
        return
    
    def setup_message(self, msg:dict[str, str]):
        # Msg should be {'name':'player', 'word':'weight', 'word':'weight',...}
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
        for player in self.players:
            player.damage = 0
            player.seen_triggers.clear()
        self.start_game()
        return
    

async def run_wordbomb(manual_input=False):
    load_environment()

    krabgor:Player = Player(player_name="KrabGor")
    alt_player:Player = Player(player_name="Player2")

    broadcaster:Broadcaster = Broadcaster(name="WORDBOMB")
    wordbomb:WordBomb = WordBomb(players=[krabgor, alt_player], repeatable_triggers=True, broadcaster=broadcaster)
    service:Games_Service = Games_Service(game=wordbomb, sub_ports=[find_port("DISCORD")], broadcaster=broadcaster, ui_enabled=manual_input)

    while not service.shutdown:
        await asyncio.sleep(5)
    return

if __name__ == "__main__":
    asyncio.run(run_wordbomb(manual_input=True))
    