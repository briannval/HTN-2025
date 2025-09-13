import os
from datetime import datetime

import cv2
from cv2_enumerate_cameras import enumerate_cameras

from modules.cohere import CohereImageAnalyzer


class CameraManager:
    def __init__(self, camera_index=0, save_dir="images", cohere_api_key=None):
        self.camera_index = camera_index
        self.save_dir = save_dir
        self.cap = None
        self.running = False
        self.cohere_analyzer = None

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
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_ANY)

            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_index}")
                return False

            self.running = True
            return True

        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def stop_camera(self):
        if self.cap:
            self.cap.release()
            self.running = False
        cv2.destroyAllWindows()

    def show_preview(self):
        if not self.running or not self.cap:
            return False

        ret, frame = self.cap.read()
        if ret:
            cv2.imshow('Camera Preview - Say "snapshot" to capture', frame)
            return True
        return False

    def take_snapshot(self):
        if not self.running or not self.cap:
            return None

        ret, frame = self.cap.read()
        if not ret:
            print("Error: Could not capture frame from camera")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.jpg"
        filepath = os.path.join(self.save_dir, filename)

        success = cv2.imwrite(filepath, frame)

        if success:
            print(f"Snapshot saved: {filepath}")
            self.show_captured_photo(filepath)

            if self.cohere_analyzer:
                try:
                    print("Analyzing image with Cohere...")
                    description = self.cohere_analyzer.describe_image_for_blind_person(
                        filepath
                    )
                    print(f"Image description: {description}")
                    return filepath, description
                except Exception as e:
                    print(f"Error analyzing image: {e}")
                    return filepath, None
            else:
                return filepath, None
        else:
            print("Error: Failed to save image")
            return None

    def show_captured_photo(self, filepath):
        img = cv2.imread(filepath)
        if img is not None:
            cv2.imshow("Captured Photo", img)
            cv2.waitKey(3000)
            cv2.destroyWindow("Captured Photo")


def list_cameras():
    cams = enumerate_cameras()
    available_cams = [(cam.index, cam.name, cam.path) for cam in cams]
    return available_cams


def select_camera():
    cameras = list_cameras()
    if not cameras:
        print("No cameras found!")
        return None

    print("Available cameras:")
    for index, name, path in cameras:
        print(f"[{index}] [{name}] {path}")

    while True:
        try:
            choice = input(f"Select camera index: ")
            camera_index = int(choice)
            if any(camera_index == idx for idx, _, _ in cameras):
                return camera_index
            else:
                print("Invalid camera index. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
