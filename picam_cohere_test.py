import os
import logging

import dotenv
from modules.pi_camera import PiCameraManager
from modules.speak import speak

logger = logging.getLogger(__name__)


def main():
    dotenv.load_dotenv()

    camera_manager = PiCameraManager(cohere_api_key=os.getenv("COHERE_API_KEY"))
    if not camera_manager.start_camera():
        logger.error("Failed to start camera. Exiting.")
        exit()

    logger.info("Taking photo")
    if camera_manager.take_photo():
        speak("Photo taken successfully")
    else:
        speak("Failed to take photo")
        return

    photo_path, description = camera_manager.analyze_photo()

    if description:
        speak("Here's what I see in the image:")
        speak(description)
    else:
        speak("Photo analysis failed")

    camera_manager.stop_camera()


main()
