import argparse
import os
import tempfile
import time
import urllib.parse
import wave

import azure.cognitiveservices.speech as speechsdk
import numpy as np
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

from utils.ml_logging import get_logger

load_dotenv()

logger = get_logger()


class SpeechTranscriber:
    """
    A class that encapsulates the Azure Cognitive Services Speech SDK functionality for transcribing speech.
    """

    def __init__(self):
        self.speech_key = os.getenv("SPEECH_KEY")
        self.speech_region = os.getenv("SPEECH_REGION")
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, region=self.speech_region
        )

    def get_blob_client_from_url(self, blob_url: str):
        """
        Retrieves a BlobClient object for the specified blob URL.

        Args:
            blob_url (str): The URL of the blob.

        Returns:
            Optional[BlobClient]: A BlobClient object for the specified blob URL, or None if the connection string is not set.
        """
        parsed_url = urllib.parse.urlparse(blob_url)
        blob_name = os.path.basename(parsed_url.path)
        container_name = os.path.basename(os.path.dirname(parsed_url.path))
        if not self.connection_string:
            logger.error("Azure storage connection string is not set.")
            return None

        blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        return blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )

    def transcribe_speech_from_file_async(self, file_name: str) -> str:
        """
        Transcribes speech from an audio file using Azure Cognitive Services Speech SDK.

        Args:
            file_name (str): The name of the audio file to transcribe.

        Returns:
            str: The transcribed text from the audio file.
        """
        audio_config = speechsdk.AudioConfig(filename=file_name)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, audio_config=audio_config
        )

        logger.info(f"Transcribing speech from file: {file_name}")
        result = speech_recognizer.recognize_once_async().get()
        return self.process_recognition_result(result)

    def process_recognition_result(self, result):
        """
        Processes the result of a speech recognition operation.

        Args:
            result (speechsdk.SpeechRecognitionResult): The result of the speech recognition operation.

        Returns:
            str: The transcribed text from the speech recognition result.
        """
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

    def transcribe_speech_from_file_continuous(self, file_name: str, language: str = None, source_language_config: speechsdk.SourceLanguageConfig = None, auto_detect_source_language_config: speechsdk.AutoDetectSourceLanguageConfig = None) -> str:
        """
        Performs continuous speech recognition with input from an audio file.

        Args:
            file_name (str): The name of the audio file to transcribe.
            language (str, optional): The language to use for speech recognition. Defaults to None.
            source_language_config (SourceLanguageConfig, optional): The source language configuration. Defaults to None.
            auto_detect_source_language_config (AutoDetectSourceLanguageConfig, optional): The auto detect source language configuration. Defaults to None.

        Returns:
            str: The transcribed text from the audio file.
        """
        audio_config = speechsdk.AudioConfig(filename=file_name)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, 
            audio_config=audio_config,
            language=language,
            source_language_config=source_language_config,
            auto_detect_source_language_config=auto_detect_source_language_config
        )

        done = False
        final_text = ""

        def update_final_text(evt):
            nonlocal final_text
            final_text += " " + evt.result.text

        def stop_cb(evt: speechsdk.SessionEventArgs):
            logger.info(f"CLOSING on {evt}")
            nonlocal done
            done = True

        speech_recognizer.recognizing.connect(
            lambda evt: logger.info(f"RECOGNIZING: {evt}")
        )
        speech_recognizer.recognized.connect(update_final_text)
        speech_recognizer.session_started.connect(
            lambda evt: logger.info(f"SESSION STARTED: {evt}")
        )
        speech_recognizer.session_stopped.connect(
            lambda evt: logger.info(f"SESSION STOPPED {evt}")
        )
        speech_recognizer.canceled.connect(lambda evt: logger.info(f"CANCELED {evt}"))
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(0.01)
        speech_recognizer.stop_continuous_recognition()

        return final_text.strip()

    def transcribe_speech_from_blob_continuous(self, blob_url: str, language: str = None, source_language_config: speechsdk.SourceLanguageConfig = None, auto_detect_source_language_config: speechsdk.AutoDetectSourceLanguageConfig = None) -> str:
        """
        Performs continuous speech recognition with input from an audio file stored in a blob.

        Args:
            blob_url (str): The URL of the blob containing the audio file to transcribe.
            language (str, optional): The language to use for speech recognition. Defaults to None.
            source_language_config (SourceLanguageConfig, optional): The source language configuration. Defaults to None.
            auto_detect_source_language_config (AutoDetectSourceLanguageConfig, optional): The auto detect source language configuration. Defaults to None.

        Returns:
            Optional[str]: The transcribed text from the audio file, or None if the blob client could not be created.
        """

        blob_client = self.get_blob_client_from_url(blob_url)
        if blob_client is None:
            return None

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            download_stream = blob_client.download_blob()
            temp_file.write(download_stream.readall())

        audio_config = speechsdk.AudioConfig(filename=temp_file.name)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, 
            audio_config=audio_config,
            language=language,
            source_language_config=source_language_config,
            auto_detect_source_language_config=auto_detect_source_language_config
        )

        done = False
        final_text = ""

        def update_final_text(evt):
            nonlocal final_text
            final_text += " " + evt.result.text

        def stop_cb(evt: speechsdk.SessionEventArgs):
            logger.info(f"CLOSING on {evt}")
            nonlocal done
            done = True

        speech_recognizer.recognizing.connect(
            lambda evt: logger.info(f"RECOGNIZING: {evt}")
        )
        speech_recognizer.recognized.connect(update_final_text)
        speech_recognizer.session_started.connect(
            lambda evt: logger.info(f"SESSION STARTED: {evt}")
        )
        speech_recognizer.session_stopped.connect(
            lambda evt: logger.info(f"SESSION STOPPED {evt}")
        )
        speech_recognizer.canceled.connect(lambda evt: logger.info(f"CANCELED {evt}"))
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(0.01)
        speech_recognizer.stop_continuous_recognition()

        try:
            os.remove(temp_file.name)
        except OSError as e:
            logger.warning(f"Error deleting temporary file: {e}")

        return final_text.strip()

    def speech_recognition_with_push_stream(self, audio_file: str, language: str = None, source_language_config: speechsdk.SourceLanguageConfig = None, auto_detect_source_language_config: speechsdk.AutoDetectSourceLanguageConfig = None):
        """
        Recognizes speech from a custom audio source using a push audio stream.
        Converts stereo audio to mono in real-time before pushing it to the stream.

        Args:
            audio_file (str): The name of the audio file to transcribe.
            language (str, optional): The language to use for speech recognition. Defaults to None.
            source_language_config (SourceLanguageConfig, optional): The source language configuration. Defaults to None.
            auto_detect_source_language_config (AutoDetectSourceLanguageConfig, optional): The auto detect source language configuration. Defaults to None.
        """
        try:
            speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key, region=self.speech_region
            )
            stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=stream)
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, 
                audio_config=audio_config,
                language=language,
                source_language_config=source_language_config,
                auto_detect_source_language_config=auto_detect_source_language_config
            )

            done = False
            wav_fh = wave.open(audio_file, "rb")
            final_text = ""

            def update_final_text(evt):
                nonlocal final_text
                final_text += " " + evt.result.text

            def stop_cb(evt):
                logger.info(f"CLOSING on {evt}")
                nonlocal done
                done = True

            speech_recognizer.recognizing.connect(
                lambda evt: logger.info(f"RECOGNIZING: {evt}")
            )
            speech_recognizer.recognized.connect(update_final_text)
            speech_recognizer.session_started.connect(
                lambda evt: logger.info(f"SESSION STARTED: {evt}")
            )
            speech_recognizer.session_stopped.connect(
                lambda evt: logger.info(f"SESSION STOPPED {evt}")
            )
            speech_recognizer.canceled.connect(
                lambda evt: logger.info(f"CANCELED {evt}")
            )
            speech_recognizer.session_stopped.connect(stop_cb)
            speech_recognizer.canceled.connect(stop_cb)

            speech_recognizer.start_continuous_recognition()

            while not done:
                frames = wav_fh.readframes(wav_fh.getframerate() // 10)
                if not frames:
                    break

                if wav_fh.getnchannels() == 2:
                    try:
                        # Interpreting the stereo frame data
                        stereo_data = np.frombuffer(frames, dtype=np.int16)
                        logger.info(f"Stereo data shape: {stereo_data.shape}")
                        # The reshape(-1, 2) method is used to ensure that the stereo data
                        # is reshaped into a 2-column array (representing left and right channels).
                        # Then, the mean is calculated across the columns (axis=1) to produce the
                        # mono audio data.
                        # Reshaping and averaging to convert to mono
                        mono_data = (
                            stereo_data.reshape(-1, 2).mean(axis=1).astype(np.int16)
                        )
                        logger.info(f"Mono data shape: {mono_data.shape}")
                        # Convert mono_data back to bytes
                        mono_frames = mono_data.tobytes()
                        stream.write(mono_frames)
                    except Exception as e:
                        logger.error(f"Error during stereo to mono conversion: {e}")
                else:
                    mono_data = np.frombuffer(frames, dtype=np.int16)
                    logger.info(f"Mono data shape: {mono_data.shape}")
                    mono_frames = mono_data.tobytes()
                    stream.write(mono_frames)

                time.sleep(0.1)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            wav_fh.close()
            stream.close()
            speech_recognizer.stop_continuous_recognition()
            return final_text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe speech from an audio file."
    )
    parser.add_argument("--file", required=True, help="The path to the audio file.")
    args = parser.parse_args()

    transcriber = SpeechTranscriber()

    if not os.path.isfile(args.file):
        logger.error(f"File {args.file} not found.")
        return

    try:
        logger.info(transcriber.transcribe_speech_from_file_continuous(args.file))
    except Exception as e:
        logger.error(f"Failed to transcribe audio file: {e}")


if __name__ == "__main__":
    main()