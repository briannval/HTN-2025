import os

import dotenv

from modules.cohere_analyzer import CohereImageAnalyzer
from modules.pi_camera import PiCameraManager
import time
from modules.listen import listen_for_snapshot_pi, list_microphone_names


def main():
    dotenv.load_dotenv()

    print("Available microphones:")
    list_microphone_names()

    dotenv.load_dotenv()
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if cohere_api_key:
        cohere_analyzer = CohereImageAnalyzer(cohere_api_key, prompt_index=2)
    else:
        print("COHERE_API_KEY environment variable not set. Exiting.")
        return

    camera_manager = PiCameraManager()
    if not camera_manager.start_camera():
        print("Failed to start camera. Exiting.")
        exit()

    time.sleep(1)

    listen_for_snapshot_pi(camera_manager, cohere_analyzer)

    camera_manager.stop_camera()

main()

