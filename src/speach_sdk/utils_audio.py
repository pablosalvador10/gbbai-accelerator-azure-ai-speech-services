import os

from pydub import AudioSegment

from utils.ml_logging import get_logger

logger = get_logger()


def log_audio_characteristics(file_name: str):
    """
    Logs the characteristics of an audio file.

    Args:
        file_name (str): The path to the audio file.

    Returns:
        None
    """
    # Check if file exists
    if not os.path.exists(file_name):
        logger.error(f"File not found: {file_name}")
        return

    try:
        # Load audio file directly without converting to a different format
        audio = AudioSegment.from_file(file_name)

        # Log basic audio information
        logger.info(f"Audio file characteristics for {file_name}:")
        logger.info(f"Number of channels: {audio.channels}")

        sample_width = audio.sample_width
        logger.info(f"Sample width (bytes): {sample_width}")

        logger.info(f"Sampling frequency (Hz): {audio.frame_rate}")

        # Calculate number of frames
        number_of_frames = len(audio)
        logger.info(f"Number of frames: {number_of_frames}")

    except Exception as e:
        logger.error(f"An error occurred while analyzing the audio file: {e}")
