import datetime
import logging
import os

import dotenv

from db.dynamo import DynamoDBInterface
from db.opensearch import OpenSearchClient
from modules.cohere_analyzer import CohereImageAnalyzer
from modules.cohere_answer import CohereAnswer
from modules.listen import listen_for_query
from modules.location import Location
from modules.pi_camera import PiCameraManager
from modules.speak import speak

logger = logging.getLogger(__name__)


class PhotoError(Exception):
    pass


class Main:
    def __init__(self, prompt_index=2):
        dotenv.load_dotenv()
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        if not self.cohere_api_key:
            logger.error("COHERE_API_KEY environment variable not set. Exiting.")
            exit(1)

        self.cohere_analyzer = CohereImageAnalyzer(self.cohere_api_key, prompt_index)
        self.cohere_answer = CohereAnswer()
        self.camera_manager = PiCameraManager()
        self.dynamo_db = DynamoDBInterface()
        self.opensearch_client = OpenSearchClient()

    def start(self):
        if not self.camera_manager.start_camera():
            raise RuntimeError("Failed to start camera. Exiting.")
        # TODO INTEGRATE BUTTON
        # one click for snapshot, two for remember
        logger.info("Taking snapshot")
        snapshotResult = self.snapshot()
        logger.info("Remembering snapshot")
        self.remember(snapshotResult)

        question = input("Ask a question: ")
        self.ask(question)

        """
        logger.info("Listening for query")
        self.query_listen()
        """

    def ask(self, question):
        try:
            speak("Thinking hard...")
            speak("Processing...")
            answer = self.cohere_answer.generate_contextual_answer(
                question,
                self.opensearch_client.get_search_by_text_results_prompt(
                    self.opensearch_client.search_by_text(question)
                ),
            )

            logger.info(f"Answer: {answer}")
            speak(answer)
        except Exception as e:
            logger.error(f"Error asking question: {str(e)}")

    # Remember the description from a snapshot
    def remember(self, desc):
        try:
            self.add_to_db(desc)
        except PhotoError as e:
            logger.error(f"Error taking photo: {str(e)}")
            speak(e)

    # Take a snapshot and describe it
    def snapshot(self):
        try:
            snapshotResult = self.take_photo()
            speak(snapshotResult)
            return snapshotResult
        except Exception as e:
            logger.error(f"Error taking photo: {str(e)}")
            speak(e)

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

    def query_listen(self):
        # Just keep listening for now
        # TODO: Integrate with button
        query = listen_for_query(True)
        res = self.opensearch_client.search_by_text(query)
        res_prompt = self.opensearch_client.get_search_by_text_results_prompt(res)
        cohere_answer = CohereAnswer()
        speak(cohere_answer.generate_contextual_answer(query, res_prompt))

    def add_to_db(self, description: str):
        time = datetime.datetime.now().isoformat()
        location = Location.get_formatted_location()
        self.dynamo_db.add_entry(time, location, description)


if __name__ == "__main__":
    main = Main()
    main.start()
