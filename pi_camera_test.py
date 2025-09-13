from modules.pi_camera import PiCameraManager

def test_pi_camera():
    camera_manager = PiCameraManager(save_dir="test_images", cohere_api_key=None)
    assert camera_manager.start_camera(), "Failed to start Pi camera"

    assert camera_manager.take_photo(), "Failed to take photo"
    assert camera_manager.saved_photo_path is not None, "Photo path should not be None"
    print(f"Photo saved at: {camera_manager.saved_photo_path}")

    camera_manager.stop_camera()
    print("Pi camera test completed successfully")

test_pi_camera()