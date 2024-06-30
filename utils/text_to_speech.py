import edge_tts
from sounddevice import play
from soundfile import read


def tts(text: str):
    edge_tts.Communicate(text, "ja-JP-NanamiNeural").save_sync("tts_output.mp3")
    play(*read("tts_output.mp3"))
