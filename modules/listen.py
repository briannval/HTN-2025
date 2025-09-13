import cv2
import speech_recognition as sr

from modules.speak import speak


def list_microphone_names():
    print(sr.Microphone.list_microphone_names())


def listen_for_snapshot(camera_manager):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source)

    print("Listening for the word 'snapshot'...")

    while True:
        with mic as source:
            audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Heard: {command}")

            if "snapshot" in command:
                print("Taking snapshot")
                speak("Taking snapshot")
                result = camera_manager.take_snapshot()

                if result:
                    if isinstance(result, tuple):
                        photo_path, description = result
                        if photo_path:
                            speak("Photo saved successfully")
                            if description:
                                print("Speaking image description...")
                                speak("Here's what I see in the image:")
                                speak(description)
                            else:
                                speak("Image analysis not available")
                        else:
                            speak("Failed to take photo")
                    else:
                        photo_path = result
                        if photo_path:
                            speak("Photo saved successfully")
                        else:
                            speak("Failed to take photo")
                else:
                    speak("Failed to take photo")

        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except sr.WaitTimeoutError:
            pass
