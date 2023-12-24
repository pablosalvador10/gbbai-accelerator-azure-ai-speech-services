import os
from typing import Optional

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from azure.cognitiveservices.speech import (
    SpeechConfig,
    SpeechSynthesisResult,
)

from utils.ml_logging import get_logger

# Set up logger
logger = get_logger()

# Load environment variables
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")


def create_speech_synthesizer(key: str, region: str) -> speechsdk.SpeechSynthesizer:
    """
    Creates a speech synthesizer with the given Azure key and region.

    Args:
        key (str): The subscription key for the Azure Speech service.
        region (str): The region for the Azure Speech service.

    Returns:
        SpeechSynthesizer: A configured speech synthesizer instance.
    """
    speech_config = SpeechConfig(subscription=key, region=region)
    audio_config = AudioOutputConfig(use_default_speaker=True)
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    return speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )


def synthesize_speech(
    text: str, synthesizer: speechsdk.SpeechSynthesizer
) -> Optional[SpeechSynthesisResult]:
    """
    Synthesizes speech from the provided text using the given speech synthesizer.

    Args:
        text (str): The text to synthesize.
        synthesizer (SpeechSynthesizer): The speech synthesizer instance to use.

    Returns:
        Optional[SpeechSynthesisResult]: The result of the speech synthesis, or None in case of failure.
    """
    try:
        logger.info(f"Synthesizing speech for text: {text[:30]}...")
        speech_synthesis_result = synthesizer.speak_text_async(text).get()

        if (
            speech_synthesis_result.reason
            == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            logger.info("Speech synthesis completed successfully.")
            return speech_synthesis_result
        else:
            logger.error("Speech synthesis failed.")
            if speech_synthesis_result.cancellation_details:
                logger.error(
                    f"Reason: {speech_synthesis_result.cancellation_details.reason}"
                )
                logger.error(
                    f"Error details: {speech_synthesis_result.cancellation_details.error_details}"
                )
            return None

    except Exception as e:
        logger.error(f"An error occurred during speech synthesis: {e}")
        return None
