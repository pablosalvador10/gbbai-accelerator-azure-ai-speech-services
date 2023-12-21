import argparse
import os
import shutil
from datetime import datetime, timedelta

from utils.ml_logging import get_logger

# Set up logger
logger = get_logger()


def delete_old_folders(base_path: str, days: int):
    """
    Delete folders in the specified path that are older than a certain number of days.

    :param base_path: Path to the directory containing subfolders.
    :param days: Number of days to use as a threshold for deleting folders.
    :return: None
    """
    try:
        today = datetime.now()
        cutoff_date = today - timedelta(days=days)

        for folder_name in os.listdir(base_path):
            # Extract the date from the folder name
            try:
                folder_date_str = folder_name.split("_")[-1]
                folder_date = datetime.strptime(folder_date_str, "%Y%m%d")
            except (IndexError, ValueError):
                logger.warning(
                    f"Skipping folder with unexpected name format: {folder_name}"
                )
                continue

            # Delete folder if it's older than the specified number of days
            if folder_date < cutoff_date:
                folder_path = os.path.join(base_path, folder_name)
                shutil.rmtree(folder_path)
                logger.info(f"Deleted folder: {folder_path}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Delete old folders.")
    parser.add_argument(
        "--base_path",
        type=str,
        required=True,
        help="The base path where the folders are located.",
    )
    parser.add_argument(
        "--days_threshold",
        type=int,
        required=True,
        help="The age threshold for folders to be deleted.",
    )

    args = parser.parse_args()

    # Call the function with the parsed arguments
    delete_old_folders(args.base_path, args.days_threshold)


# Call the main function
if __name__ == "__main__":
    main()
