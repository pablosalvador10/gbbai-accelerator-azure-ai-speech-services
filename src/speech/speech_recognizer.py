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

# Load environment variables
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")


def recognize_from_microphone(
    key: str, region: str
) -> Tuple[str, Optional[SpeechRecognitionResult]]:
    """
    Recognizes speech from the microphone.

    Args:
        key (str): The subscription key for the Speech service.
        region (str): The region for the Speech service.

    Returns:
        Tuple[str, Optional[SpeechRecognitionResult]]: The recognized text and the result object.
    """
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_recognition_language = "en-US"

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
            logger.error("Error details: {}".format(cancellation_details.error_details))
            logger.error("Did you set the speech resource key and region values?")

    # Return the recognized text and the result object
    return speech_recognition_result.text, speech_recognition_result
