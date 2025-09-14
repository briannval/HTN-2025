import time

import speech_recognition as sr

from modules.speak import speak


def start_listening():

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source)

    print("Listening for keywords 'snapshot' or 'recall'...")
    speak("Ready. Say 'snapshot' to take a photo or 'recall' to ask a question.")

    while True:
        with mic as source:
            try:
                audio = recognizer.listen(source, timeout=5)
            except sr.WaitTimeoutError:
                continue

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Heard: {command}")

            if "snapshot" in command:
                print("Taking snapshot")
                print("Snapshot command detected")
                speak("Taking snapshot")
                # snapshot_result = self.snapshot()
                # self.remember(snapshot_result)

            elif "recall" in command:
                print("Recall command detected")
                speak("What would you like to recall?")
                time.sleep(2)

                # Listen for the follow-up query
                with mic as source:
                    try:
                        query_audio = recognizer.listen(source, timeout=20)
                        query = recognizer.recognize_google(query_audio).lower()
                        print(f"Query: {query}")
                        speak(f"Processing your query: {query}")
                        # self.ask(query)
                    except (
                        sr.UnknownValueError,
                        sr.WaitTimeoutError,
                        sr.RequestError,
                    ):
                        speak(
                            "Sorry, I didn't understand your question. Please try again."
                        )

        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except sr.WaitTimeoutError:
            pass


if __name__ == "__main__":
    start_listening()
