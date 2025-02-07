import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = "ai_pipeline.log"

def setup_logger():
    """
    Sets up a global logger for all scripts with both file and console logging.
    - Uses **rotating logs** to prevent unlimited file growth.
    - Logs messages to both the **file** and the **console**.
    """
    logger = logging.getLogger("AI_Pipeline_Logger")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers when importing this in multiple scripts
    if not logger.hasHandlers():
        # File Logging (Rotates at 5MB, keeps last 5 logs)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        # Console Logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# ✅ Global logger instance
logger = setup_logger()
