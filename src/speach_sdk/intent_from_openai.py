import os
import json
import argparse
from typing import Optional
from utils.ml_logging import get_logger
from src.speach_sdk.speach_to_text import transcribe_speech_from_file_continuous
import openai
from dotenv import load_dotenv
load_dotenv()

# Set up logger
logger = get_logger()

# Load environment variables
SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')

# Load config values
with open(r'src/speach_sdk/aoai_config.json') as config_file:
    config_details = json.load(config_file)

# Set up OpenAI API
openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_KEY")
openai.api_base = config_details['OPENAI_API_BASE']
openai.api_version = config_details['OPENAI_API_VERSION']

# Set up deployment name
deployment_name = config_details['COMPLETIONS_MODEL']

def generate_text_completion(prompt: str, temperature: float = 0.5, max_tokens: int = 100, deployment_name: str = "foundational-instruct") -> Optional[str]:
    """
    Generates a text completion using Foundation models from OpenAI.
    """
    try:
        completion = openai.Completion.create(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            engine=deployment_name
        )

        logger.info(completion.choices[0].text.strip(" \n"))

        if completion.choices[0].finish_reason == "content_filter":
            logger.warning("The generated content is filtered.")

        return completion.choices[0].text.strip(" \n")

    except openai.error.APIError as e:
        logger.error(f"OpenAI API returned an API Error: {e}")
    except openai.error.AuthenticationError as e:
        logger.error(f"OpenAI API returned an Authentication Error: {e}")
    except openai.error.APIConnectionError as e:
        logger.error(f"Failed to connect to OpenAI API: {e}")
    except openai.error.InvalidRequestError as e:
        logger.error(f"Invalid Request Error: {e}")
    except openai.error.RateLimitError as e:
        logger.error(f"OpenAI API request exceeded rate limit: {e}")
    except openai.error.ServiceUnavailableError as e:
        logger.error(f"Service Unavailable: {e}")
    except openai.error.Timeout as e:
        logger.error(f"Request timed out: {e}")

def transcribe_and_analyze_speech(): 
    """
    Transcribes speech from an audio file and analyzes it using OpenAI.
    """
    parser = argparse.ArgumentParser(description='Transcribe speech from an audio file.')
    parser.add_argument("--file", required=True, help="The path to the audio file.")
    args = parser.parse_args()
    
    #TODO: add config support
    TEMPERATURE = 0.7
    MAX_TOKENS = 100

    try:
        prompt = transcribe_speech_from_file_continuous(args.file, key=SPEECH_KEY, region=SPEECH_REGION)
        logger.info(prompt)
    except Exception as e:
        logger.error(f"Failed to transcribe audio file: {e}")
        return

    try:
        
        if prompt is None: 
            logger.error("Failed to transcribe audio file.")
            return 

        BASE_PROMPT = f'''Act as pharmaceutilcal expert and analyze the following conversation {prompt}, please
        Focus on identifying the Intent/Goal from the customer related to their inquiry. 
        After analyzing the conversation, provide a concise summary.'''

        logger.info(f"Input Prompt: {BASE_PROMPT}")

        response = generate_text_completion(BASE_PROMPT, temperature=TEMPERATURE, max_tokens=MAX_TOKENS, deployment_name=deployment_name)
    except Exception as e:
        logger.error(f"Failed to generate text completion: {e}")
        return


if __name__ == '__main__':
    transcribe_and_analyze_speech()