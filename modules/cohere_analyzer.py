import base64
import os
from typing import Optional

import cohere

AYA_VISION_MODEL = "c4ai-aya-vision-32b"


class CohereImageAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Cohere API key is required. Set COHERE_API_KEY environment variable or pass it directly."
            )

        self.client = cohere.ClientV2(self.api_key)
        self.model = AYA_VISION_MODEL

    def encode_image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            base64_image_url = f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode('utf-8')}"
            return base64_image_url

    def describe_image_for_blind_person(self, image_path: str) -> str:
        try:
            image_base64 = self.encode_image_to_base64(image_path)

            prompt = """Please describe this image in detail as if you were describing it to a blind person. Include:
1. The main objects and people in the scene
2. Their positions and spatial relationships
3. Colors, lighting, and mood
4. Any text that appears in the image
5. Activities or actions taking place
6. The overall setting or environment

Be descriptive and specific, but also very concise, keeping at most 30 words, focusing on visual details that would help someone who cannot see understand what's happening in the image."""

            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_base64}},
                        ],
                    }
                ],
            )

            return response.message.content[0].text

        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def get_simple_description(self, image_path: str) -> str:
        try:
            image_base64 = self.encode_image_to_base64(image_path)

            prompt = "Briefly describe what you see in this image in 1-2 sentences."

            response = self.client.chat(
                message=prompt,
                model="command-r-plus",
                documents=[
                    {"id": "image", "content": image_base64, "mime_type": "image/jpeg"}
                ],
            )

            return response.text

        except Exception as e:
            return f"Error analyzing image: {str(e)}"


if __name__ == "__main__":
    pass
