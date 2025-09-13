from picamera2 import Picamera2, Preview
import time
import os
from modules.cohere import CohereImageAnalyzer


class PiCameraManager:
    def __init__(self, save_dir="images", cohere_api_key=None):
        self.save_dir = save_dir
        self.cohere_analyzer = None
        self.cam = None
        self.saved_photo_path = None

        if cohere_api_key:
            try:
                self.cohere_analyzer = CohereImageAnalyzer(cohere_api_key)
                print("Cohere image analyzer initialized successfully")
            except Exception as e:
                print(f"Warning: Could not initialize Cohere analyzer: {e}")
                self.cohere_analyzer = None

    def start_camera(self):
        try:
            os.makedirs(self.save_dir, exist_ok=True)
            self.cam = Picamera2()

            camera_config = self.cam.create_preview_configuration()
            self.cam.configure(camera_config)

            self.cam.start_preview(Preview.QTGL)
            self.cam.start()
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def stop_camera(self):
        if self.cam:
            self.cam.stop_preview()
            self.cam.close()
            self.cam = None

    def take_photo(self):
        if not self.cam:
            print("Error: Camera not started")
            return False

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        photo_path = os.path.join(self.save_dir, f"snapshot_{timestamp}.jpg")

        try:
            self.cam.capture_file(photo_path)
            self.saved_photo_path = photo_path
            print(f"Photo saved to {photo_path}")
            return True
        except Exception as e:
            print(f"Error taking photo: {e}")
            return False

    def analyze_photo(self):
        if not self.saved_photo_path or not self.cohere_analyzer:
            return None

        try:
            print("Analyzing image with Cohere...")
            description = self.cohere_analyzer.describe_image_for_blind_person(
                self.saved_photo_path
            )
            print(f"Image description: {description}")
            return self.saved_photo_path, description
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return self.saved_photo_path, None

