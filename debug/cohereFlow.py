def cohereFlow(camera_manager):
    result, _ = camera_manager.take_snapshot()
    camera_manager.cohere_analyzer.describe_image_for_blind_person(
        result
    )  # debug workflow
