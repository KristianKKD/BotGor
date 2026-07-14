import keyboard
import mouse
import asyncio    

DEFAULT_TIME_MS:int = 500
MAX_TIME_MS:int = 5000

DEFAULT_COUNT:int = 1
MAX_COUNT:int = 5

KEYBOARD_INPUTS:dict[str, str] = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",

    "lookleft": "left",
    "lookright": "right",
    "lookup": "up",
    "lookdown": "down",

    "jump": "space",
}

MOUSE_INPUTS:dict[str] = {
    "crank" : "right",
    "krabgo1crank" : "right",
    "kill"  : "left"
}

class IO_Handler:
    def __init__(self):
        return

    async def process_twitch_input(self, content:str) -> list[str]:
        def process_time(cmd:str) -> int:
            time_ms:int = DEFAULT_TIME_MS
            if ':' in cmd:
                _, time_part = cmd.strip().split(':', 1)
                try:
                    time_ms = int(time_part.strip())
                except ValueError:
                    pass
            if time_ms < 0 : time_ms = DEFAULT_TIME_MS
            if time_ms > MAX_TIME_MS : time_ms = MAX_TIME_MS
            return time_ms
        
        def process_count(cmd:str) -> int:
            count:int = DEFAULT_COUNT
            if 'x' in cmd:
                _, count_str = cmd.split('x', 1)
                try:
                    count = int(count_str.strip())
                except ValueError:
                    pass
            if count < 0 : count = DEFAULT_COUNT
            if count > MAX_COUNT : count = MAX_COUNT
            return count

        commands:list[str] = [c.strip().lower() for c in content.split(' ') if c.strip()]
        all_inputs:dict[str] = MOUSE_INPUTS + KEYBOARD_INPUTS

        command:str
        for command in commands:
            if command not in all_inputs:
                continue

            is_mouse:bool = command in MOUSE_INPUTS
            target_key:str = all_inputs[command]
            time_ms:int = process_time(command)
            count:int = process_count(command)

            print(f"PRESSING {target_key} for {str(time_ms)}ms, {str(count)} times")
            asyncio.create_task(self._input(is_mouse=is_mouse, key=target_key, time_ms=time_ms, count=count))
        return

    async def _input(self, is_mouse:bool, key:str, time_ms:int, count:int):
        for _ in range(count):
            if is_mouse == "keyboard":
                mouse.release(button=key)
                mouse.press(button=key)
                await asyncio.sleep(time_ms/1000)
                mouse.release(button=key)
            else:
                keyboard.release(key)
                keyboard.press(key)
                await asyncio.sleep(time_ms/1000)
                keyboard.release(key)
        return