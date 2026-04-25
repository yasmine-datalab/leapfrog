"""Logger Config"""

import os
import glob
import logging

from .config import settings


# 1. Configure Logging (Globally):
def configure_logging():
    """Configure logging for whole app"""

    app_name = settings.API_TITLE.replace(" ", "-").lower()
    log_level = settings.LOG_LEVEL
    log_file_pattern = f"{app_name}_*.log"  # Pattern for log files
    log_dir = "logs"  # Directory to store logs

    # Create the log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Find the highest existing log number to increment from
    existing_logs = glob.glob(os.path.join(log_dir, log_file_pattern))
    max_log_number = 0
    for log_file in existing_logs:
        try:
            number = int(log_file.split("_")[-1].split(".")[0])  # Extract number
            max_log_number = max(max_log_number, number)
        except ValueError:
            pass  # Ignore files that don't match the numbering pattern

    new_log_number = max_log_number + 1
    log_file_name = os.path.join(log_dir, f"{app_name}_{new_log_number}.log")

    handlers = [
        logging.StreamHandler(),
    ]

    if settings.ENV != "developement":
        handlers.append(logging.FileHandler(log_file_name))
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


logger = logging.getLogger(__name__)