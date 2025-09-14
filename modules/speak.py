import os
import tempfile
import threading

import playsound
from gtts import gTTS

# If you get namespace GST not found, do sudo apt get install gstreamer-1.0


def _speak_sync(text):
    """Internal synchronous speak function."""
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang="en")
        tts.save(fp.name)
        playsound.playsound(fp.name)


def speak(text):
    """Non-blocking speak function that runs in a background thread."""
    thread = threading.Thread(target=_speak_sync, args=(text,))
    thread.start()
    return thread
