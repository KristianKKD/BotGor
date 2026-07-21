from abc import ABC, abstractmethod
from threading import Thread, Event
from time import sleep

LOOP_GAME:int = 0
EVENT_GAME:int = 1

class Game(ABC):
    def __init__(self, game_type:int=EVENT_GAME, loop_time_s:float = 0.5):
        self.pause_event:Event = Event()
        self.stop_event:Event = Event()
        self.time_between_loops_s:float = loop_time_s

        self.game_type:int = game_type
        if game_type == LOOP_GAME:
            self.game_thread:Thread = Thread(target=self.game_loop(), daemon=True)
        return
    
    def start_game(self):
        self.stop_event.clear()
        self.game_thread.start()
        return
    
    def pause_game(self):
        self.pause_event.set()
        return
    
    def resume_game(self):
        self.pause_event.clear()
        return

    def stop_game(self):
        self.stop_event.set()
        self.pause_event.clear()
        if self.game_type == LOOP_GAME:
            self.game_thread.join()
        return

    def game_loop(self, **kwargs):
        while not self.stop_event.is_set():
            if not self.pause_event.is_set():
                self.game_event(**kwargs)

            sleep(self.time_between_loops_s)
        return
    
    def setup_message(self, msg:dict[str, str]):
        """Handle setup messages, should be triggered before game start but doesn't have to be. Optionally can be implemented by subclasses"""
        return

    @abstractmethod
    def game_event(self, **kwargs):
        """
        Game event called every tick within game_loop OR MANUALLY FOR EVERY EVENT.
        LOOP_GAME starts handling inputs after handler calls start_games, which starts game_loop.
        EVENT_GAME requires this method to be called for processing.
        Can be paused with pause_game and resumed with resume_game.
        Can be stopped with stop_game.
        Must be implemented by subclasses. Should handle starting, pausing, and stopping if EVENT_GAME.
        """
        return

    @abstractmethod
    def incoming_message(self, msg:dict[str, str]):
        """Handle general messages such as game events. Must be implemented by subclasses."""
        return

    @abstractmethod
    def reset_game(self):
        """Reset game to initial state, recommended to trigger start_game afterwards. Must be implemented by subclasses."""
        return
