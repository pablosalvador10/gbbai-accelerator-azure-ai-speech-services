import os
import time

from src.aoai.intent_azure_openai import AzureOpenAIAssistant
from src.speech.speech_recognizer import recognize_from_microphone
from src.speech.text_to_speech import synthesize_speech
from utils.ml_logging import get_logger

# Set up logger
logger = get_logger()

az_openai_client = AzureOpenAIAssistant()

# Load environment variables
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

# Define stop words and silence threshold
STOP_WORDS = ["goodbye", "exit", "stop", "see you later", "bye"]
SILENCE_THRESHOLD = 20  # in seconds

def check_for_stopwords(prompt: str) -> bool:
    """
    Check if the given prompt contains any predefined stop words.

    Args:
        prompt (str): The prompt to check.

    Returns:
        bool: True if any stop word is found, False otherwise.
    """
    return any(stop_word in prompt.lower() for stop_word in STOP_WORDS)

def handle_speech_recognition() -> str:
    """
    Handles speech recognition from the microphone.

    Returns:
        str: The recognized speech as text.
    """
    logger.info("Recognizing speech from microphone...")
    prompt, _ = recognize_from_microphone(SPEECH_KEY, SPEECH_REGION)
    return prompt

def main():
    """
    Main function to recognize speech from microphone, generate text completion using OpenAI,
    and synthesize speech from the generated text. Stops on specific words or prolonged silence.
    """
    try:
        conversation_history = []
        last_speech_time = time.time()

        while True:
            prompt = handle_speech_recognition()

            if prompt:
                last_speech_time = time.time()  # Reset the silence timer
                logger.info(f"Recognized prompt: {prompt}")

                if check_for_stopwords(prompt):
                    logger.info("Stop word detected, exiting...")
                    synthesize_speech("Goodbye.", SPEECH_KEY, SPEECH_REGION)
                    break

                response = az_openai_client.generate_text_with_contextual_history(
                    conversation_history, prompt, deployment_name="foundational-canadaeast-gpt4"
                )

                if response:
                    logger.info(f"Generated response: {response}")
                    synthesize_speech(response, SPEECH_KEY, SPEECH_REGION)
                else:
                    logger.warning("No response generated.")
            elif time.time() - last_speech_time > SILENCE_THRESHOLD:
                logger.info(f"No speech detected for over {SILENCE_THRESHOLD} seconds, exiting...")
                synthesize_speech(f"No speech detected for over {SILENCE_THRESHOLD} seconds. Goodbye.", SPEECH_KEY, SPEECH_REGION)
                break
            else:
                logger.warning("No prompt recognized.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
