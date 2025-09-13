from modules.gemini_tts import generate_and_play
import time
import dotenv
from google import genai
import os


def test_tts():
    input_text = """
    This image captures a wide, sunlit view of a university campus, likely during a beautiful day. In the foreground, there's a prominent, tall clock tower with a dark, square clock face, rising high above the surrounding buildings. To the right of the clock tower, a grand, ornate stone building with intricate architectural details and multiple windows stands out. Its facade has a historic and academic feel.
The campus is lush with greenery, featuring numerous trees with vibrant green foliage scattered throughout the grounds. Several other modern and traditional buildings of varying heights can be seen in the background, including a taller, multi-story building on the far left with many windows.
The sky is bright and clear, dominated by a brilliant sun emitting a warm, golden glow from the upper right corner of the frame, casting a soft, golden light across the entire scene. There are also some subtle hints of clouds in the sky, adding texture. The overall impression is one of an expansive, well-maintained, and active university environment bathed in beautiful natural light."""
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    generate_and_play(client, input_text)


dotenv.load_dotenv()

test_tts()
