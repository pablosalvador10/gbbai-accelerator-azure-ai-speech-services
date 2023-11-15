import azure.cognitiveservices.speech as speechsdk
import time 
import os
from utils.ml_logging import get_logger
import argparse
from typing import List
from src.speach_sdk.utils_audio import log_audio_characteristics
from dotenv import load_dotenv
load_dotenv()
logger = get_logger()

KEY = os.getenv('KEY_SPEACH')
REGION = os.getenv('REGION')
language_understanding_app_id = os.getenv('INTENT_KEY')

def aggregate_and_determine_intent(recognized_intents):
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
        intent_id = intent.get('intent_id')
        if intent_id:
            intent_counts[intent_id] = intent_counts.get(intent_id, 0) + 1

    return intent_counts

def recognize_intent_continuous(file_name: str, key: str, region: str, intents_list: List[str]) -> str:
    """
    Performs continuous intent recognition from input from an audio file.
    Uses the Azure Cognitive Services Speech SDK to set up an intent recognizer,
    add intents to be recognized, and start continuous recognition.
    Returns the final recognized text.

    Args:
        file_name (str): The name of the audio file to transcribe.
        key (str): The subscription key for the Speech service.
        region (str): The region for the Speech service.
    """
    logger.info("Starting continuous intent recognition...")
    log_audio_characteristics(file_name)
    intent_config = speechsdk.SpeechConfig(subscription=key, region=region)
    audio_config = speechsdk.audio.AudioConfig(filename=file_name)
    intent_recognizer = speechsdk.intent.IntentRecognizer(speech_config=intent_config, audio_config=audio_config)

    # Set up the intents to be recognized
    model = speechsdk.intent.LanguageUnderstandingModel(app_id=language_understanding_app_id)
    intents = [
        (model, "HomeAutomation.TurnOn"),
        (model, "HomeAutomation.TurnOff")] + intents_list
    
    intent_recognizer.add_intents(intents)

    recognized_intents = []

    def on_intent_recognized(evt: speechsdk.intent.IntentRecognitionEventArgs):
        recognized_intents.append({
            'intent_id': evt.result.intent_id,
            'text': evt.result.text
        })
        logger.info("RECOGNIZED: Intent Id: {}, Text: {}".format(evt.result.intent_id, evt.result.text))

    intent_recognizer.recognized.connect(on_intent_recognized)

    done = False

    def stop_cb(evt: speechsdk.SessionEventArgs):
        logger.info('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    # Connect callbacks to the events
    intent_recognizer.session_started.connect(lambda evt: logger.info("SESSION_START: {}".format(evt)))
    intent_recognizer.recognizing.connect(lambda evt: logger.info("RECOGNIZING: {}".format(evt)))
    intent_recognizer.canceled.connect(lambda evt: logger.info(f"CANCELED: {evt.cancellation_details} ({evt.reason})"))
    intent_recognizer.session_stopped.connect(stop_cb)
    intent_recognizer.canceled.connect(stop_cb)

    # Start continuous intent recognition
    intent_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.05)

    # Stop continuous recognition
    intent_recognizer.stop_continuous_recognition()

    # Determine the most prominent intent
    final_intent = aggregate_and_determine_intent(recognized_intents)
    print(recognized_intents)
    logger.info(f"Final intent determined: {final_intent}")
    logger.info("Finished continuous intent recognition.")
    return final_intent
    

def recognize_intent_once_from_file(file_name: str, key: str, region: str, intents_list: List[str]) -> None:
    """
    Performs one-shot intent recognition from input from an audio file.
    Uses the Azure Cognitive Services Speech SDK to set up an intent recognizer,
    add intents to be recognized, and start the intent recognition.
    Prints the output of the recognition to the console.

    Args:
        audio_file (str): The name of the audio file to transcribe.
        intents_list (List[str]): The list of intents to be recognized.
    """
    logger.info("Starting one-shot intent recognition...")

    intent_config = speechsdk.SpeechConfig(subscription=key, region=region)
    audio_config = speechsdk.audio.AudioConfig(filename=file_name)

    intent_recognizer = speechsdk.intent.IntentRecognizer(speech_config=intent_config, audio_config=audio_config)

    model = speechsdk.intent.LanguageUnderstandingModel(app_id=language_understanding_app_id)
    intents = [(model, "HomeAutomation.TurnOn"),
        (model, "HomeAutomation.TurnOff")] + intents_list
    intent_recognizer.add_intents(intents)

    # Starts intent recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    intent_result = intent_recognizer.recognize_once()

    # Check the results
    if intent_result.reason == speechsdk.ResultReason.RecognizedIntent:
        logger.info("Recognized: \"{}\" with intent id `{}`".format(intent_result.text, intent_result.intent_id))
    elif intent_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        logger.info("Recognized: {}".format(intent_result.text))
    elif intent_result.reason == speechsdk.ResultReason.NoMatch:
        logger.info("No speech could be recognized: {}".format(intent_result.no_match_details))
    elif intent_result.reason == speechsdk.ResultReason.Canceled:
        logger.info("Intent recognition canceled: {}".format(intent_result.cancellation_details.reason))
        if intent_result.cancellation_details.reason == speechsdk.CancellationReason.Error:
            logger.error("Error details: {}".format(intent_result.cancellation_details.error_details))
    # </IntentRecognitionOnceWithFile>
    logger.info("Finished one-shot intent recognition.")


def main():
    parser = argparse.ArgumentParser(description="Recognize intent from an audio file.")
    parser.add_argument("--file", required=True, help="The path to the audio file.")
    args = parser.parse_args()
    
    #TODO: Remote
    if not os.path.isfile(args.file):
        logger.error(f"File {args.file} not found.")
        return
    
    intent_list = [
      ("What is the {weather}?", "queryMeteorology"),
      ("What is the {date}?", "queryDate"),
    ]

    recognize_intent_continuous(args.file, KEY, REGION, intent_list)

    #recognize_intent_once_from_file(args.file, KEY, REGION, intent_list)

if __name__ == "__main__":
    main()