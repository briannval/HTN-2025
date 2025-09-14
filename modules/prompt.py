def cohere_prompt(index: int) -> str:
    prompts_list = [
        """
        Please describe this image in detail as if you were describing it to a blind person. Include:
        1. The main objects and people in the scene
        2. Their positions and spatial relationships
        3. Colors, lighting, and mood
        4. Any text that appears in the image
        5. Activities or actions taking place
        6. The overall setting or environment
    
        Be descriptive and specific, but also very concise, keeping at most 30 words, focusing on visual details that would help a visually impaired person understand what is happening in the image.
        """,
        """
        Describe this image in detail as if you were describing it to a blind person. Include:
        1. The main objects and people in the foreground and their relative positions in frame
        2. The background elements and their relative positions in frame
        3. Activities or actions taking place
        4. Colours and lighting
        5. Any text that appears in the image
        
        Be descriptive and specific, but also very concise, keeping at most 30 words, focusing on visual details that would help a visually impaired person understand what is happening in the image.
        """
    ]
    if index < 0 or index >= len(prompts_list):
        index = 0
    return prompts_list[index]