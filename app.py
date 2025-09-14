import os
import time
import sys

import dotenv

from modules.cohere_analyzer import CohereImageAnalyzer
from modules.pi_camera import PiCameraManager
from modules.speak import speak
from db.dynamo import DynamoDBInterface
from datetime import datetime

DYNAMO_DB = DynamoDBInterface()


def main():
    try:
        prompt_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    except ValueError:
        prompt_index = 0

    dotenv.load_dotenv()
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if cohere_api_key:
        cohere_analyzer = CohereImageAnalyzer(cohere_api_key, prompt_index=prompt_index)
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
    description = camera_manager.analyze_photo(cohere_analyzer)

    if description:
        speak("Here's what I see in the image:")
        speak(description)
    else:
        speak("Photo analysis failed")

    time = datetime.now().isoformat()
    location = Location.get_location()
    DYNAMO_DB.add_entry(time, location, description)


if __name__ == "__main__":
    main()
