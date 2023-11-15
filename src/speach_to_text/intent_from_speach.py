import azure.cognitiveservices.speech as speechsdk
import time 
import os
from utils.ml_logging import get_logger
import argparse
from dotenv import load_dotenv
load_dotenv()
logger = get_logger()


KEY = os.getenv('KEY')
REGION = os.getenv('REGION')
language_understanding_app_id = os.getenv('INTENT_KEY')


def recognize_intent_continuous(file_name: str, key: str, region: str) -> None:
    """
    Performs continuous intent recognition from input from an audio file.
    Uses the Azure Cognitive Services Speech SDK to set up an intent recognizer,
    add intents to be recognized, and start continuous recognition.
    Prints the output of the recognition to the console.

    Args:
        file_name (str): The name of the audio file to transcribe.
        key (str): The subscription key for the Speech service.
        region (str): The region for the Speech service.
    """
    # Set up the intent recognizer
    intent_config: speechsdk.SpeechConfig = speechsdk.SpeechConfig(subscription=key, region=region)
    audio_config: speechsdk.audio.AudioConfig = speechsdk.audio.AudioConfig(filename=file_name)
    intent_recognizer: speechsdk.intent.IntentRecognizer = speechsdk.intent.IntentRecognizer(speech_config=intent_config, audio_config=audio_config)

    # set up the intents that are to be recognized. These can be a mix of simple phrases and
    # intents specified through a LanguageUnderstanding Model.
    model = speechsdk.intent.LanguageUnderstandingModel(app_id=language_understanding_app_id)
    intents = [
        (model, "HomeAutomation.TurnOn"),
        (model, "HomeAutomation.TurnOff"),
        ("This is a test.", "test"),
        ("Switch the channel to 34.", "34"),
        ("what's the weather like", "weather"),
    ]
    intent_recognizer.add_intents(intents)

    # Connect callback functions to the signals the intent recognizer fires.
    done = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    intent_recognizer.session_started.connect(lambda evt: print("SESSION_START: {}".format(evt)))
    intent_recognizer.speech_end_detected.connect(lambda evt: print("SPEECH_END_DETECTED: {}".format(evt)))
    # event for intermediate results
    intent_recognizer.recognizing.connect(lambda evt: print("RECOGNIZING: {}".format(evt)))
    # event for final result
    intent_recognizer.recognized.connect(lambda evt: print(
        "RECOGNIZED: {}\n\tText: {} (Reason: {})\n\tIntent Id: {}\n\tIntent JSON: {}".format(
            evt, evt.result.text, evt.result.reason, evt.result.intent_id, evt.result.intent_json)))

    # cancellation event
    intent_recognizer.canceled.connect(lambda evt: print(f"CANCELED: {evt.cancellation_details} ({evt.reason})"))

    # stop continuous recognition on session stopped, end of speech or canceled events
    intent_recognizer.session_stopped.connect(stop_cb)
    intent_recognizer.speech_end_detected.connect(stop_cb)
    intent_recognizer.canceled.connect(stop_cb)

    # And finally run the intent recognizer. The output of the callbacks should be printed to the console.
    intent_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)

    intent_recognizer.stop_continuous_recognition()
    # </IntentContinuousRecognitionWithFile>