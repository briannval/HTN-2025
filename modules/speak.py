import os
import tempfile

import playsound
from gtts import gTTS

# If you get namespace GST not found, do sudo apt get install gstreamer-1.0


def speak(text):
    # Create a temporary mp3 file
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang="en")
        tts.save(fp.name)
        playsound.playsound(fp.name)
