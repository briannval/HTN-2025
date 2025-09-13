import os
import time

import dotenv

from modules.cohere_analyzer import CohereImageAnalyzer
from modules.pi_camera import PiCameraManager
from modules.speak import speak


def main():
    dotenv.load_dotenv()
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if cohere_api_key:
        cohere_analyzer = CohereImageAnalyzer(cohere_api_key)
    else:
        print("COHERE_API_KEY environment variable not set. Exiting.")
        return

    camera_manager = PiCameraManager()
    if not camera_manager.start_camera():
        print("Failed to start camera. Exiting.")
        exit()

    time.sleep(2)

    print("Taking photo")
    if camera_manager.take_photo():
        speak("Photo taken successfully")
    else:
        speak("Failed to take photo")
        camera_manager.stop_camera()
        return

    camera_manager.stop_camera()
    photo_path, description = camera_manager.analyze_photo(cohere_analyzer)

    if description:
        speak("Here's what I see in the image:")
        speak(description)
    else:
        speak("Photo analysis failed")


main()
