import pyttsx3
from gemini_tts import generate_and_play


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def speak_with_gemini(text):
    generate_and_play(text)
