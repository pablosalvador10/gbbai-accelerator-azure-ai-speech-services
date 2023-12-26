import os
from typing import Optional, Tuple

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechRecognitionResult
from dotenv import load_dotenv

from utils.ml_logging import get_logger

# Set up logger
logger = get_logger()

# Load environment variables from .env file
load_dotenv()


class SpeechRecognizer:
    """
    A class that encapsulates the Azure Cognitive Services Speech SDK functionality for recognizing speech.
    """

    def __init__(self, key: str = None, region: str = None, language: str = "en-US"):
        """
        Initializes a new instance of the SpeechRecognizer class.

        Args:
            key (str, optional): The subscription key for the Speech service. Defaults to the SPEECH_KEY environment variable.
            region (str, optional): The region for the Speech service. Defaults to the SPEECH_REGION environment variable.
            language (str, optional): The language for the Speech service. Defaults to "en-US".
        """
        self.key = key if key is not None else os.getenv("SPEECH_KEY")
        self.region = region if region is not None else os.getenv("SPEECH_REGION")
        self.language = language

    def recognize_from_microphone(
        self,
    ) -> Tuple[str, Optional[SpeechRecognitionResult]]:
        """
        Recognizes speech from the microphone.

        Returns:
            Tuple[str, Optional[SpeechRecognitionResult]]: The recognized text and the result object.
        """
        speech_config = speechsdk.SpeechConfig(
            subscription=self.key, region=self.region
        )
        speech_config.speech_recognition_language = self.language

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        logger.info("Speak into your microphone.")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info("Recognized: {}".format(speech_recognition_result.text))
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            logger.warning(
                "No speech could be recognized: {}".format(
                    speech_recognition_result.no_match_details
                )
            )
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            logger.error(
                "Speech Recognition canceled: {}".format(cancellation_details.reason)
            )
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.error(
                    "Error details: {}".format(cancellation_details.error_details)
                )
                logger.error("Did you set the speech resource key and region values?")

        # Return the recognized text and the result object
        return speech_recognition_result.text, speech_recognition_result
