import os
from typing import Optional

import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesisResult
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from dotenv import load_dotenv

from utils.ml_logging import get_logger

# Set up logger
logger = get_logger()

# Load environment variables from .env file
load_dotenv()


class SpeechSynthesizer:
    def __init__(self, key: str = None, region: str = None):
        self.key = key if key is not None else os.getenv("SPEECH_KEY")
        self.region = region if region is not None else os.getenv("SPEECH_REGION")
        self.synthesizer = self.create_speech_synthesizer()

    def create_speech_synthesizer(self) -> speechsdk.SpeechSynthesizer:
        """
        Creates a speech synthesizer with the given Azure key and region.
        """
        speech_config = SpeechConfig(subscription=self.key, region=self.region)
        audio_config = AudioOutputConfig(use_default_speaker=True)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

        return speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )

    def synthesize_speech(self, text: str) -> Optional[SpeechSynthesisResult]:
        """
        Synthesizes speech from the provided text using the Azure Speech SDK.

        This method uses the SpeechSynthesizer instance created during the initialization of the class.
        It converts the input text into speech and returns the result as a SpeechSynthesisResult object.
        If the synthesis fails for any reason, it returns None and logs the error details.

        Args:
            text (str): The text to be converted into speech.

        Returns:
            Optional[SpeechSynthesisResult]: The result of the speech synthesis operation, or None if the synthesis failed.
        """
        try:
            logger.info(f"Synthesizing speech for text: {text[:30]}...")
            speech_synthesis_result = self.synthesizer.speak_text_async(text).get()

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
