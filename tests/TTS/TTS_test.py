import sys
import asyncio

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

def test_tts_system():
    from TTS.TTS_Engines.TTS_System import TTS_System
    
    tts_a = TTS_System(id=0)
    assert tts_a.speak(text="A", user="User", output_file=False)

    tts_b = TTS_System(id=1)
    assert tts_b.speak(text="B", user="User", output_file=False)

    return

def test_handler():
    from TTS.TTS_Handler import TTS_Handler
    from TTS.TTS_Engines.TTS_System import TTS_System

    tts = TTS_Handler(TTS_System(id=0))
    asyncio.run(tts.speak(text="one", user="Testing"))
    asyncio.run(tts.speak(text="two", user="Testing"))

    return

if __name__ == "__main__":
    asyncio.run(test_handler())