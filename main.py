import datetime
import logging
import os
import time

import speech_recognition as sr

import dotenv

from db.dynamo import DynamoDBInterface
from db.opensearch import OpenSearchClient
from modules.cohere_analyzer import CohereImageAnalyzer
from modules.cohere_answer import CohereAnswer
from modules.location import Location
from modules.pi_camera import PiCameraManager
from modules.speak import speak

logger = logging.getLogger(__name__)


class PhotoError(Exception):
    pass


class Main:
    def __init__(self, prompt_index=3):
        dotenv.load_dotenv()
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        if not self.cohere_api_key:
            print("COHERE_API_KEY environment variable not set. Exiting.")
            exit(1)

        self.cohere_analyzer = CohereImageAnalyzer(self.cohere_api_key, prompt_index)
        self.cohere_answer = CohereAnswer()
        self.camera_manager = PiCameraManager()
        self.dynamo_db = DynamoDBInterface()
        self.opensearch_client = OpenSearchClient()

    def start(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source)

        print("Listening for keywords 'snapshot' or 'recall'...")
        speak("Ready. Say 'snapshot' to take a photo or 'recall' to ask a question.")

        while True:
            with mic as source:
                try:
                    audio = recognizer.listen(source, timeout=5)
                except sr.WaitTimeoutError:
                    continue

            try:
                command = recognizer.recognize_google(audio).lower()
                print(f"Heard: {command}")

                if "snapshot" in command:
                    if not self.camera_manager.start_camera():
                        raise RuntimeError("Failed to start camera. Exiting.")
                    print("Taking snapshot")
                    print("Snapshot command detected")
                    speak("Taking snapshot")
                    snapshot_result = self.snapshot()
                    self.remember(snapshot_result)

                elif "recall" in command:
                    print("Recall command detected")
                    speak("What would you like to recall?")
                    time.sleep(2)

                    # Listen for the follow-up query
                    with mic as source:
                        try:
                            query_audio = recognizer.listen(source, timeout=20)
                            query = recognizer.recognize_google(query_audio).lower()
                            print(f"Query: {query}")
                            speak(f"Processing your query: {query}")
                            self.ask(query)
                        except (
                                sr.UnknownValueError,
                                sr.WaitTimeoutError,
                                sr.RequestError,
                        ):
                            speak(
                                "Sorry, I didn't understand your question. Please try again."
                            )

            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except sr.WaitTimeoutError:
                pass

    def ask(self, question):
        try:
            answer = self.cohere_answer.generate_contextual_answer(
                question,
                self.opensearch_client.get_search_by_text_results_prompt(
                    self.opensearch_client.search_by_text(question)
                ),
            )

            print(f"Answer: {answer}")
            speak(answer)
        except Exception as e:
            print(f"Error asking question: {str(e)}")

    # Remember the description from a snapshot
    def remember(self, desc):
        try:
            self.add_to_db(desc)
        except PhotoError as e:
            print(f"Error taking photo: {str(e)}")
            speak(str(e))

    # Take a snapshot and describe it
    def snapshot(self):
        try:
            snapshotResult = self.take_photo()
            speak(snapshotResult)
            return snapshotResult
        except PhotoError as e:
            print(f"Error taking photo: {str(e)}")
            speak(str(e))

    # Take snapshot and return its description
    def take_photo(self) -> str:
        print("Taking photo")
        if self.camera_manager.take_photo():
            speak("Photo taken successfully")
        else:
            self.camera_manager.stop_camera()
            raise PhotoError("Failed to take photo")

        self.camera_manager.stop_camera()
        result = self.camera_manager.analyze_photo(self.cohere_analyzer)
        if result:
            return result
        else:
            raise PhotoError("Photo analysis failed")

    def add_to_db(self, description: str):
        formatted_time = datetime.datetime.now().isoformat()
        location = Location.get_formatted_location()
        self.dynamo_db.add_entry(formatted_time, location, description)


if __name__ == "__main__":
    main = Main()
    main.start()
