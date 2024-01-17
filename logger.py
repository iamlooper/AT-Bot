import logging
from logging.handlers import RotatingFileHandler
import os
import shutil

from config import (
    LOG_FILE,
    ENABLE_LOGGER
)

MAX_LOG_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# Configure logger.
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level=logging.INFO)

# Create file handler for logging.
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILE)

def setup_logging():
    # Add rotating file handler to the logger.
    file_handler = RotatingFileHandler(log_file_path, maxBytes=MAX_LOG_FILE_SIZE, backupCount=1)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    LOGGER.addHandler(file_handler)

# Create or touch an empty log file.
if not os.path.exists(log_file_path):
    with open(log_file_path, 'a'):
        os.utime(log_file_path, None)

# Initialize logging setup.
setup_logging()

def write_log_info(*text):
    # Write log messages with info level.
    if ENABLE_LOGGER:
        for string in text:
            LOGGER.info(string)

def write_log_warning(*text):
    # Write log messages with warning level.
    if ENABLE_LOGGER:
        for string in text:
            LOGGER.warning(string)

_PREFIX_FUNC_DIC = {
    "info": ("[*]", write_log_info),
    "warning": ("[!]", write_log_warning),
}

def print_and_log(string, level="info", custom_prefix=None):
    """
    Print to terminal and write to log simultaneously.
    :param string: The string to print
    :param level: Log level
    :param custom_prefix: Custom string prefix
    """
    prefix, log_func = _PREFIX_FUNC_DIC.get(level, ("[*]", write_log_info))
    if custom_prefix is not None:
        prefix = custom_prefix
    if prefix:
        print(prefix, string)
    else:
        print(string)
    log_func(string)