from modules.cohere_analyzer import CohereImageAnalyzer
from modules.server import ESP32Server


def cohereFlow():
    esp32_server = ESP32Server()
    esp32_server.start()
    esp32_server.request_frame()
    # MANUAL result, _ = camera_manager.take_snapshot()
    print("Describing image...")
    cohere_analyzer = CohereImageAnalyzer()
    print(
        cohere_analyzer.describe_image_for_blind_person("received_frame.jpg")
    )  # debug workflow
    esp32_server.close()
