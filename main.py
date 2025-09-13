import argparse
import os

import dotenv

from modules.gemini_tts import generate_and_play
from debug.cohereFlow import cohereFlow
from modules.camera import CameraManager, select_camera
from modules.listen import list_microphone_names, listen_for_snapshot


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--DEBUG_COHERE", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    dotenv.load_dotenv()
    args = parse_args()

    print("Available microphones:")
    list_microphone_names()

    camera_index = select_camera()
    if camera_index is None:
        print("No camera selected. Exiting.")
        exit()

    cohere_api_key = os.getenv("COHERE_API_KEY")
    if not cohere_api_key:
        print(
            "Warning: COHERE_API_KEY environment variable not set. Image analysis will not be available."
        )
        print("To enable image analysis, set your Cohere API key:")
        print("export COHERE_API_KEY='your_api_key_here'")
    else:
        print("Cohere API key found. Image analysis will be available.")

    camera_manager = CameraManager(camera_index, cohere_api_key=cohere_api_key)
    if not camera_manager.start_camera():
        print("Failed to start camera. Exiting.")
        exit()

    try:
        if args.DEBUG_COHERE:
            cohereFlow(camera_manager)
        else:
            listen_for_snapshot(camera_manager)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        camera_manager.stop_camera()
