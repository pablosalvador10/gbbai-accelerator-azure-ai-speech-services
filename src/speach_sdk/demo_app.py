from src.speach_sdk.speach_recognizer import recognize_from_microphone
from src.speach_sdk.intent_from_openai import generate_text_completion
from src.speach_sdk.text_to_speach import synthesize_speech
from utils.ml_logging import get_logger
import os

# Set up logger
logger = get_logger()

# Set up logger
logger = get_logger()

# Load environment variables
SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')

def main():
    """
    Main function to recognize speech from microphone, generate text completion using OpenAI, 
    and synthesize speech from the generated text.
    """
    try:
        logger.info("Recognizing speech from microphone...")
        prompt, _ = recognize_from_microphone(SPEECH_KEY,SPEECH_REGION)
        if prompt:
            logger.info(f"Recognized prompt: {prompt}")
            logger.info("Generating text completion...")
            response = generate_text_completion(prompt)
            if response:
                logger.info(f"Generated response: {response}")
                logger.info("Synthesizing speech from response...")
                synthesize_speech(response,SPEECH_KEY,SPEECH_REGION)
            else:
                logger.warning("No response generated.")
        else:
            logger.warning("No prompt recognized.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()