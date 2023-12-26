import argparse
import os
import time
from typing import List

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

from src.speech.utils_audio import log_audio_characteristics
from utils.ml_logging import get_logger

load_dotenv()
logger = get_logger()


class IntentRecognizer:
    """
    A class that encapsulates the Azure Cognitive Services Lenguage SDK functionality for recognizing intents.
    """

    def __init__(self, key: str = None, region: str = None, app_id: str = None):
        """
        Initializes a new instance of the IntentRecognizer class.

        Args:
            key (str, optional): The subscription key for the Speech service. Defaults to the SPEECH_KEY environment variable.
            region (str, optional): The region for the Speech service. Defaults to the SPEECH_REGION environment variable.
            app_id (str, optional): The app id for the Language Understanding Model. Defaults to the INTENT_KEY environment variable.
        """
        self.key = key if key is not None else os.getenv("SPEECH_KEY")
        self.region = region if region is not None else os.getenv("SPEECH_REGION")
        self.app_id = app_id if app_id is not None else os.getenv("INTENT_KEY")

    @staticmethod
    def aggregate_and_determine_intent(recognized_intents: List[dict]) -> dict:
        """
        Analyzes recognized intents and creates a dictionary with the count of times each intent was detected.

        Args:
            recognized_intents (List[dict]): A list of recognized intents.

        Returns:
            dict: A dictionary with intents as keys and their counts as values.
        """
        if not recognized_intents:
            return {}

        intent_counts = {}
        for intent in recognized_intents:
            intent_id = intent.get("intent_id")
            if intent_id:
                intent_counts[intent_id] = intent_counts.get(intent_id, 0) + 1

        return intent_counts

    def recognize_intent_continuous(
        self, file_name: str, intents_list: List[str]
    ) -> str:
        """
        Performs continuous intent recognition from input from an audio file.
        Uses the Azure Cognitive Services Speech SDK to set up an intent recognizer,
        add intents to be recognized, and start continuous recognition.
        Returns the final recognized text.

        Args:
            file_name (str): The name of the audio file to transcribe.
            intents_list (List[str]): The list of intents to be recognized.
        """
        logger.info("Starting continuous intent recognition...")
        log_audio_characteristics(file_name)
        intent_config = speechsdk.SpeechConfig(
            subscription=self.key, region=self.region
        )
        audio_config = speechsdk.audio.AudioConfig(filename=file_name)
        intent_recognizer = speechsdk.intent.IntentRecognizer(
            speech_config=intent_config, audio_config=audio_config
        )

        # Set up the intents to be recognized
        model = speechsdk.intent.LanguageUnderstandingModel(app_id=self.app_id)
        intents = [
            (model, "HomeAutomation.TurnOn"),
            (model, "HomeAutomation.TurnOff"),
        ] + intents_list

        intent_recognizer.add_intents(intents)

        recognized_intents = []

        def on_intent_recognized(evt: speechsdk.intent.IntentRecognitionEventArgs):
            recognized_intents.append(
                {"intent_id": evt.result.intent_id, "text": evt.result.text}
            )
            logger.info(
                f"RECOGNIZED: Intent Id: {evt.result.intent_id}, Text: {evt.result.text}"
            )

        intent_recognizer.recognized.connect(on_intent_recognized)

        done = False

        def stop_cb(evt: speechsdk.SessionEventArgs):
            logger.info(f"CLOSING on {evt}")
            nonlocal done
            done = True

        # Connect callbacks to the events
        intent_recognizer.session_started.connect(
            lambda evt: logger.info(f"SESSION_START: {evt}")
        )
        intent_recognizer.recognizing.connect(
            lambda evt: logger.info(f"RECOGNIZING: {evt}")
        )
        intent_recognizer.canceled.connect(
            lambda evt: logger.info(
                f"CANCELED: {evt.cancellation_details} ({evt.reason})"
            )
        )
        intent_recognizer.session_stopped.connect(stop_cb)
        intent_recognizer.canceled.connect(stop_cb)

        # Start continuous intent recognition
        intent_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(0.05)

        # Stop continuous recognition
        intent_recognizer.stop_continuous_recognition()

        # Determine the most prominent intent
        final_intent = self.aggregate_and_determine_intent(recognized_intents)
        logger.info(f"Final intent determined: {final_intent}")
        logger.info("Finished continuous intent recognition.")
        return final_intent

    def recognize_intent_once_from_file(
        self, file_name: str, intents_list: List[str]
    ) -> None:
        """
        Performs one-shot intent recognition from input from an audio file.
        Uses the Azure Cognitive Services Speech SDK to set up an intent recognizer,
        add intents to be recognized, and start the intent recognition.
        Prints the output of the recognition to the console.

        Args:
            file_name (str): The name of the audio file to transcribe.
            intents_list (List[str]): The list of intents to be recognized.
        """
        logger.info("Starting one-shot intent recognition...")

        intent_config = speechsdk.SpeechConfig(
            subscription=self.key, region=self.region
        )
        audio_config = speechsdk.audio.AudioConfig(filename=file_name)

        intent_recognizer = speechsdk.intent.IntentRecognizer(
            speech_config=intent_config, audio_config=audio_config
        )

        model = speechsdk.intent.LanguageUnderstandingModel(app_id=self.app_id)
        intents = [
            (model, "HomeAutomation.TurnOn"),
            (model, "HomeAutomation.TurnOff"),
        ] + intents_list
        intent_recognizer.add_intents(intents)

        # Starts intent recognition, and returns after a single utterance is recognized.
        intent_result = intent_recognizer.recognize_once()

        # Check the results
        if intent_result.reason == speechsdk.ResultReason.RecognizedIntent:
            logger.info(
                f'Recognized: "{intent_result.text}" with intent id `{intent_result.intent_id}`'
            )
        elif intent_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info(f"Recognized: {intent_result.text}")
        elif intent_result.reason == speechsdk.ResultReason.NoMatch:
            logger.info(
                f"No speech could be recognized: {intent_result.no_match_details}"
            )
        elif intent_result.reason == speechsdk.ResultReason.Canceled:
            logger.info(
                f"Intent recognition canceled: {intent_result.cancellation_details.reason}"
            )
            if (
                intent_result.cancellation_details.reason
                == speechsdk.CancellationReason.Error
            ):
                logger.error(
                    f"Error details: {intent_result.cancellation_details.error_details}"
                )
        logger.info("Finished one-shot intent recognition.")


def main():
    parser = argparse.ArgumentParser(description="Recognize intent from an audio file.")
    parser.add_argument("--file", required=True, help="The path to the audio file.")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        logger.error(f"File {args.file} not found.")
        return

    intent_list = [
        ("What is the {weather}?", "queryMeteorology"),
        ("What is the {date}?", "queryDate"),
    ]

    # Create an instance of the IntentRecognizer class
    intent_recognizer = IntentRecognizer()

    try:
        # Call the recognize_intent_continuous method of the intent_recognizer object
        intent_recognizer.recognize_intent_continuous(args.file, intent_list)
    except Exception as e:
        logger.error(f"Failed to recognize intent: {e}")

    try:
        # Call the recognize_intent_once_from_file method of the intent_recognizer object
        intent_recognizer.recognize_intent_once_from_file(args.file, intent_list)
    except Exception as e:
        logger.error(f"Failed to recognize intent: {e}")


if __name__ == "__main__":
    main()
