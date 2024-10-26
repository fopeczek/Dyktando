import os

from gtts import gTTS
from pydub import AudioSegment


class TextToAudio:
    def __init__(self):
        pass

    def convert(self, text: str) -> AudioSegment:
        tts = gTTS(text, lang="pl")
        tts.save("tmp.mp3")
        audio = AudioSegment.from_mp3("tmp.mp3")
        os.remove("tmp.mp3")
        return audio
