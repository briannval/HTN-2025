from picamera2 import Picamera2, Preview
import time
import os


class PiCameraManager:
    def __init__(self, save_dir="images"):
        self.save_dir = save_dir
        self.cam = None
        self.saved_photo_path = None

    def start_camera(self):
        try:
            os.makedirs(self.save_dir, exist_ok=True)
            self.cam = Picamera2()

            camera_config = self.cam.create_preview_configuration()
            self.cam.configure(camera_config)

            self.cam.start_preview(Preview.QTGL)
            self.cam.start()
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

    def analyze_photo(self, cohere_analyzer):
        if not self.saved_photo_path or not cohere_analyzer:
            return None

        try:
            print("Analyzing image with Cohere...")
            description = cohere_analyzer.describe_image_for_blind_person(
                self.saved_photo_path
            )
            print(f"Image description: {description}")
            return self.saved_photo_path, description
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return self.saved_photo_path, None

    # Returns the description if successful or an error message if not
    def take_and_analyze_photo(self, cohere_analyzer) -> str:
        if self.take_photo():
            _, description = self.analyze_photo(cohere_analyzer)

            if not description:
                return "Photo analysis failed"

            return "Here's what I see: " + description
        else:
            return "Failed to take photo"


