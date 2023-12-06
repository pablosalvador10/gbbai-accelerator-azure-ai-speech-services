import os
from typing import Optional

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesisResult

from utils.ml_logging import get_logger

# Set up logger
logger = get_logger()

# Load environment variables
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")


def synthesize_speech(
    text: str, key: str, region: str
) -> Optional[SpeechSynthesisResult]:
    """
    Synthesizes speech from the provided text.

    Args:
        text (str): The text to synthesize.
        key (str): The subscription key for the Speech service.
        region (str): The region for the Speech service.

    Returns:
        Optional[SpeechSynthesisResult]: The result of the speech synthesis.
    """
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    logger.info(f"Synthesizing speech for text: {text}")
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioCompleted
    ):
        logger.info(f"Speech synthesized for text [{text}]")
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        logger.error(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                logger.error(f"Error details: {cancellation_details.error_details}")
                logger.error("Did you set the speech resource key and region values?")

    return speech_synthesis_result
