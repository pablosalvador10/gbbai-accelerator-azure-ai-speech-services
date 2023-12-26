import os
import wave

from pydub import AudioSegment

from utils.ml_logging import get_logger

logger = get_logger()


def check_audio_file(file_path):
    """
    Checks the format of the audio stream from the provided WAV file and logs the details.
    Returns False if any of the required conditions are not met. Otherwise, returns True.

    Required conditions for the audio format:
    - PCM format (int-16, signed)
    - One channel (mono)
    - 16 bits per sample
    - 8,000 or 16,000 samples per second (16,000 bytes or 32,000 bytes per second)
    - Two-block aligned (16 bits including padding for a sample)

    Parameters:
    file_path (str): Path to the WAV file to be checked.
    """
    with wave.open(file_path, "rb") as wav_file:
        (
            n_channels,
            sampwidth,
            framerate,
            nframes,
            comptype,
            compname,
        ) = wav_file.getparams()

        # Check PCM format (int-16)
        is_pcm_format = comptype == "NONE" and sampwidth == 2
        logger.info(f"PCM Format (int-16): {is_pcm_format}")

        # Check if it's mono
        is_mono = n_channels == 1
        logger.info(f"One Channel (Mono): {is_mono}")

        # Check sample rate
        is_valid_sample_rate = framerate in [8000, 16000]
        logger.info(f"Valid Sample Rate (8000 or 16000 Hz): {is_valid_sample_rate}")

        # Calculate bytes per second
        bytes_per_second = framerate * sampwidth * n_channels
        logger.info(f"Bytes Per Second (16000 or 32000): {bytes_per_second}")

        # Check two-block alignment
        is_two_block_aligned = wav_file.getsampwidth() * n_channels == 2
        logger.info(f"Two-block Aligned: {is_two_block_aligned}")

        # Return False if any condition is not met
        return (
            is_pcm_format and is_mono and is_valid_sample_rate and is_two_block_aligned
        )


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
        logger.info(f"Sampling frequency (Hz): {audio.frame_rate}")

        # Calculate number of frames
        number_of_frames = len(audio)
        logger.info(f"Number of frames: {number_of_frames}")

    except Exception as e:
        logger.error(f"An error occurred while analyzing the audio file: {e}")
