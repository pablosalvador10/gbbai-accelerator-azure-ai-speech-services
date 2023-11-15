from typing import Optional
import os
from utils.ml_logging import get_logger
from pydub import AudioSegment
from pydub.utils import mediainfo
logger = get_logger()

def log_audio_characteristics(file_name: str) -> Optional[None]:
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
        audio = AudioSegment.from_file(file_name)
        base_name, _ = os.path.splitext(file_name)
        pcm_file_name = base_name + ".pcm"

        audio.export(pcm_file_name, format="wav")
        info = mediainfo(pcm_file_name)

        logger.info(f"Audio file characteristics for {pcm_file_name}:")
        logger.info(f"Number of channels: {info['channels']}")
        if info['bits_per_sample'].isdigit():
            sample_width = int(info['bits_per_sample']) / 8
            logger.info(f"Sample width (bytes): {sample_width}")
        else:
            logger.error("Invalid bits_per_sample value")
        logger.info(f"Sampling frequency (Hz): {info['sample_rate']}")
        if info['duration'].replace('.', '', 1).isdigit() and info['sample_rate'].isdigit():
            number_of_frames = int(float(info['duration']) * int(info['sample_rate']))
            logger.info(f"Number of frames: {number_of_frames}")
        else:
            logger.error("Invalid duration or sample rate values")
    except Exception as e:
        logger.error(f"An error occurred: {e}")