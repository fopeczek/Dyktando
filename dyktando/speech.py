from io import BytesIO

from gtts import gTTS
from pydub import AudioSegment
import os

class TextToAudio:
    def __init__(self):
        pass

    def convert(self, text: str) -> AudioSegment:
        # tts = gTTS(text, lang="pl")
        # mp3_fp = BytesIO()
        # tts.write_to_fp(mp3_fp)
        # audio = AudioSegment.from_file(mp3_fp, format="mp3")
        # return audio
        #
        tts = gTTS(text, lang="pl")
        tts.save("tmp.mp3")
        audio = AudioSegment.from_mp3("tmp.mp3")
        os.remove("tmp.mp3")
        return audio
