import azure.cognitiveservices.speech as speechsdk
import time 
import os
from utils.ml_logging import get_logger
from src.speach_sdk.utils_audio import log_audio_characteristics
import argparse
from dotenv import load_dotenv
load_dotenv()

logger = get_logger()

SPEECH_KEY = os.getenv('KEY_SPEACH')
SPEECH_REGION = os.getenv('REGION')

def transcribe_speech_from_file_async(file_name: str, key: str, region: str) -> str:
    """
    Transcribes speech from an audio file using Azure Cognitive Services Speech SDK.

    Args:
        file_name (str): The name of the audio file to transcribe.
        key (str): The subscription key for the Speech service.
        region (str): The region for the Speech service.

    Returns:
        str: The transcribed text from the audio file.
    """
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    audio_config = speechsdk.AudioConfig(filename=file_name)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    logger.info(f"Transcribing speech from file: {file_name}")
    result = speech_recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        logger.info(f"Transcription result: {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        logger.warning(f"No speech could be recognized: {result.no_match_details}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        logger.error(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            logger.error(f"Error details: {cancellation_details.error_details}")
    return result.text

def transcribe_speech_from_file_continuous(file_name: str, key: str, region: str) -> str:
    """performs continuous speech recognition with input from an audio file"""
    # Set up logging
  
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    audio_config = speechsdk.audio.AudioConfig(filename=file_name)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    log_audio_characteristics(file_name)

    done = False
    final_text = ""

    def update_final_text(evt):
        nonlocal final_text
        final_text += ' ' + evt.result.text

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        logger.info('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(lambda evt: logger.info('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(update_final_text)
    speech_recognizer.session_started.connect(lambda evt: logger.info('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: logger.info('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: logger.info('CANCELED {}'.format(evt)))
    # Stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.01)

    speech_recognizer.stop_continuous_recognition()

    return final_text.strip() 

def main():
    parser = argparse.ArgumentParser(description='Transcribe speech from an audio file.')
    parser.add_argument("--file", required=True, help="The path to the audio file.")
    args = parser.parse_args()
    
    if not os.path.isfile(args.file):
        logger.error(f"File {args.file} not found.")
        return

    try:
        logger.info(transcribe_speech_from_file_continuous(args.file, SPEECH_KEY, SPEECH_REGION))
    except Exception as e:
        logger.error(f"Failed to transcribe audio file: {e}")

if __name__ == '__main__':
    main()