import logging
from logging.handlers import RotatingFileHandler

from constants import LOG_FILE, MAX_BYTES, BACKUP_COUNT


# Logging Configuration
def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a file handler to store logs (with rotation)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
    file_handler.setFormatter(log_formatter)

    # Create a logger and set level to DEBUG (you can adjust it based on your needs)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)


# Call setup_logging when the app starts
setup_logging()
