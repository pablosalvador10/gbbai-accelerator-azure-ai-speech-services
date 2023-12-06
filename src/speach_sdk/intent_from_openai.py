import argparse
import json
import os
from typing import Optional

import openai
from dotenv import load_dotenv

from src.speach_sdk.speach_to_text import transcribe_speech_from_file_continuous
from utils.ml_logging import get_logger

load_dotenv()

# Set up logger
logger = get_logger()

# Load environment variables
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

# Load config values
with open(r"src/speach_sdk/aoai_config.json") as config_file:
    config_details = json.load(config_file)

# Set up OpenAI API
openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_KEY")
openai.api_base = config_details["OPENAI_API_BASE"]
openai.api_version = config_details["OPENAI_API_VERSION"]

# Set up deployment name
deployment_name = config_details["COMPLETIONS_MODEL"]


def generate_text_completion(
    prompt: str,
    temperature: float = 0.5,
    max_tokens: int = 100,
    deployment_name: str = "foundational-instruct",
) -> Optional[str]:
    """
    Generates a text completion using Foundation models from OpenAI.
    """
    try:
        completion = openai.Completion.create(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            engine=deployment_name,
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


def generate_text_with_contextual_history(
    conversation_history,
    latest_prompt,
    temperature=0.7,
    max_tokens=800,
    deployment_name="foundational-35-turbo",
):
    """
    Generates a text response using Foundation models from OpenAI, considering the conversation history as context but focusing on the latest prompt.
    Ensures the AI always understands its role as an assistant.
    """
    try:
        # Ensure the AI's role is always understood
        system_message = {
            "role": "system",
            "content": "You are an AI assistant that helps people find information.",
        }
        if not conversation_history or conversation_history[0] != system_message:
            conversation_history.insert(0, system_message)

        # Prepare messages for the API request
        messages_for_api = conversation_history + [
            {"role": "user", "content": latest_prompt}
        ]

        logger.info(f"Sending request to OpenAI with prompt: {latest_prompt}")

        # Generate response
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=messages_for_api,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Extract response content
        response_content = response["choices"][0]["message"]["content"]

        logger.info(f"Received response from OpenAI: {response_content}")

        # Update conversation history with the AI's response
        conversation_history.append({"role": "user", "content": latest_prompt})
        conversation_history.append({"role": "system", "content": response_content})

        return response_content

    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API returned an error: {e}")


def transcribe_and_analyze_speech():
    """
    Transcribes speech from an audio file and analyzes it using OpenAI.
    """
    parser = argparse.ArgumentParser(
        description="Transcribe speech from an audio file."
    )
    parser.add_argument("--file", required=True, help="The path to the audio file.")
    args = parser.parse_args()

    # TODO: add config support
    TEMPERATURE = 0.7
    MAX_TOKENS = 100

    try:
        prompt = transcribe_speech_from_file_continuous(
            args.file, key=SPEECH_KEY, region=SPEECH_REGION
        )
        logger.info(prompt)
    except Exception as e:
        logger.error(f"Failed to transcribe audio file: {e}")
        return

    try:
        if prompt is None:
            logger.error("Failed to transcribe audio file.")
            return

        BASE_PROMPT = f"""Act as pharmaceutilcal expert and analyze the following conversation {prompt}, please
        Focus on identifying the Intent/Goal from the customer related to their inquiry. 
        After analyzing the conversation, provide a concise summary."""

        logger.info(f"Input Prompt: {BASE_PROMPT}")

        response = generate_text_completion(
            BASE_PROMPT,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            deployment_name=deployment_name,
        )
        return response
    except Exception as e:
        logger.error(f"Failed to generate text completion: {e}")
        return


if __name__ == "__main__":
    transcribe_and_analyze_speech()
