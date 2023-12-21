import argparse
import os
from typing import List, Optional

import openai
from dotenv import load_dotenv

from src.speech.speech_to_text import transcribe_speech_from_file_continuous
from utils.ml_logging import get_logger

# Load environment variables from .env file
load_dotenv()

# Set up logger
logger = get_logger()


class AzureOpenAIAssistant:
    def __init__(self):
        # Load environment variables
        self.speech_key = os.getenv("SPEECH_KEY")
        self.speech_region = os.getenv("SPEECH_REGION")
        self.openai_key = os.getenv("OPENAI_KEY")

        # Check if environment variables are not empty
        if not all([self.speech_key, self.speech_region, self.openai_key]):
            raise ValueError("One or more environment variables are empty.")

        # Set up OpenAI API
        # Set up OpenAI API
        openai.api_type = "azure"
        openai.api_key = self.openai_key
        openai.api_base = os.getenv("OPENAI_API_BASE")
        openai.api_version = os.getenv("OPENAI_API_VERSION")
        self.deployment_completion_name = os.getenv("COMPLETION_MODEL")
        self.deployment_chat_name = os.getenv("CHAT_MODEL")

        # Check if OpenAI API setup variables are not empty
        if not all(
            [
                openai.api_key,
                openai.api_base,
                openai.api_version,
                self.deployment_completion_name,
                self.deployment_chat_name,
            ]
        ):
            raise ValueError("One or more OpenAI API setup variables are empty.")

    def generate_text_completion(
        self,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 100,
        deployment_completion_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generates a text completion using Foundation models from OpenAI.

        Args:
            prompt (str): The input text prompt for the model.
            temperature (float, optional): Controls randomness in the output. Default to 0.5.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 100.
            deployment_instruct_name (str, optional): The name of the AI model deployment to use. Defaults to "foundational-instruct".

        Returns:
            Optional[str]: The generated text or None if an error occurs.
        """
        try:
            completion = openai.Completion.create(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                engine=deployment_completion_name or self.deployment_completion_name,
            )

            generated_text = completion.choices[0].text.strip(" \n")
            logger.info(f"Generated text: {generated_text}")

            if completion.choices[0].finish_reason == "content_filter":
                logger.warning("The generated content is filtered.")

            return generated_text

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API returned an error: {e}")
            return None

    def generate_text_with_contextual_history(
        self,
        conversation_history: List[dict],
        latest_prompt: str,
        system_message_content: str = "You are an AI assistant that helps people find information. Please be very precise, polite, and concise.",
        temperature: float = 0.7,
        max_tokens: int = 150,
    ) -> Optional[str]:
        """
        Generates a text response using Foundation models from OpenAI, considering the conversation history as context and focusing on the latest prompt.

        Args:
            conversation_history (List[dict]): A list of message dictionaries representing the conversation history.
            latest_prompt (str): The latest prompt to generate a response for.
            system_message_content (str, optional): The content of the system message. Defaults to "You are an AI assistant that helps people find information. Please be very precise, polite, and concise."
            temperature (float, optional): Controls randomness in the output. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 150.

        Returns:
            Optional[str]: The generated text response or None if an error occurs.
        """
        try:
            system_message = {
                "role": "system",
                "content": system_message_content,
            }
            if not conversation_history or conversation_history[0] != system_message:
                conversation_history.insert(0, system_message)

            messages_for_api = conversation_history + [
                {"role": "user", "content": latest_prompt}
            ]
            logger.info(f"Sending request to OpenAI with prompt: {latest_prompt}")

            response = openai.ChatCompletion.create(
                engine=self.deployment_chat_name,
                messages=messages_for_api,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            response_content = response["choices"][0]["message"]["content"]
            logger.info(f"Received response from OpenAI: {response_content}")

            conversation_history.append({"role": "user", "content": latest_prompt})
            conversation_history.append({"role": "system", "content": response_content})

            return response_content
        except Exception as e:
            logger.error(f"Failed to generate text with contextual history: {e}")
            return None

    def summarize_and_classify_intent(
        self,
        text: str,
        temperature: float = 0.7,
        max_tokens: int = 300,
    ) -> Optional[str]:
        """
        Uses GPT-XX to provide a concise, professional summary and intent classification of the provided text.

        Args:
            text (str): The text to be summarized and classified.
            temperature (float, optional): Controls randomness in the output. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 300.

        Returns:
            Optional[str]: The summary and intent classification or None if an error occurs.
        """
        try:
            prompt = (
                f"Task: Read the following text and perform two actions. First, provide a concise, professional summary. "
                f"Second, analyze and clearly state the primary intent of the text.\n\n"
                f"---\n\n"
                f"Text:\n{text}\n\n"
                f"---\n\n"
                f"Summary and Intent Classification:"
            )

            logger.info(f"LLM Model Prompt: {prompt}")

            response_text = self.generate_text_completion(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                deployment_completion_name=self.deployment_completion_name,
            )

            logger.info(f"LLM Model Response: {response_text}")

            return response_text

        except Exception as e:
            logger.error(
                f"Failed to generate text completion with {self.deployment_completion_name}: {e}"
            )
            return None


def transcribe_summarize_and_gather_intent_from_audio_file() -> Optional[str]:
    """
    Transcribes speech from an audio file, summarizes it, and identifies its intent.

    Returns:
        str: The response from the assistant, or None if the operation failed.
    """
    assistant = AzureOpenAIAssistant()
    parser = argparse.ArgumentParser(
        description="Transcribe speech from an audio file and analyze it."
    )
    parser.add_argument("--file", required=True, help="The path to the audio file.")
    args = parser.parse_args()

    transcription = transcribe_speech_from_file_continuous(
        file_name=args.file, key=assistant.speech_key, region=assistant.speech_region
    )
    if transcription:
        logger.info(f"Transcription successful. Transcribed text: {transcription}")
    else:
        logger.error("Failed to transcribe speech from the provided audio file.")
        return None

    response = assistant.summarize_and_classify_intent(transcription)
    if response:
        logger.info(
            f"Summarization and intent classification successful. Response: {response}"
        )
        return response
    else:
        logger.error(
            "Failed to summarize and classify intent from the transcribed text."
        )
        return None


if __name__ == "__main__":
    transcribe_summarize_and_gather_intent_from_audio_file()
