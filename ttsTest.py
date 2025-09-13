from modules.gemini_tts import generate_and_play


def test_tts():
    input_text = "Hello, this is a test of the Gemini TTS system."
    generate_and_play(input_text)


test_tts()
