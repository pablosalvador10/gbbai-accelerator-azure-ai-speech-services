import os
import time

from src.speech_sdk.intent_from_openai import generate_text_with_contextual_history
from src.speech_sdk.speech_recognizer import recognize_from_microphone
from src.speech_sdk.text_to_speech import synthesize_speech
from utils.ml_logging import get_logger

# Set up logger
logger = get_logger()

# Load environment variables
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

# Define stop words and silence threshold
STOP_WORDS = ["goodbye", "exit", "stop", "see you later", "bye"]
SILENCE_THRESHOLD = 20  # in seconds


def main():
    """
    Main function to recognize speech from microphone, generate text completion using OpenAI,
    and synthesize speech from the generated text. Stops on specific words or prolonged silence.
    """
    try:
        CONVERSATION_HISTORY = []
        last_speech_time = time.time()

        while True:
            logger.info("Recognizing speech from microphone...")
            prompt, _ = recognize_from_microphone(SPEECH_KEY, SPEECH_REGION)

            if prompt:
                last_speech_time = time.time()  # Reset the silence timer
                logger.info(f"Recognized prompt: {prompt}")

                # Check for stop words
                if any(stop_word in prompt.lower() for stop_word in STOP_WORDS):
                    logger.info("Stop word detected, exiting...")
                    response = "Goodbye."
                    synthesize_speech(response, SPEECH_KEY, SPEECH_REGION)
                    break

                logger.info("Generating text completion...")
                response = generate_text_with_contextual_history(
                    CONVERSATION_HISTORY,
                    prompt,
                    deployment_name="foundational-canadaeast-gpt4",
                )

                if response:
                    logger.info(f"Generated response: {response}")
                    logger.info("Synthesizing speech from response...")
                    synthesize_speech(response, SPEECH_KEY, SPEECH_REGION)
                    last_speech_time = time.time()
                else:
                    logger.warning("No response generated.")

            elif time.time() - last_speech_time > SILENCE_THRESHOLD:
                logger.info(
                    f"No speech detected for over {SILENCE_THRESHOLD} seconds, exiting..."
                )
                response = (
                    f"No speech detected for over {SILENCE_THRESHOLD} seconds.Goodbye."
                )
                synthesize_speech(response, SPEECH_KEY, SPEECH_REGION)
                break
            else:
                logger.warning("No prompt recognized.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
