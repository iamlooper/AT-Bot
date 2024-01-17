import logging
import os

from config import (
    LOG_FILE, 
    ENABLE_LOGGER
)

# Configure logger.
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level=logging.INFO)

# Create file handler for logging.
_HANDLER = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILE))
_HANDLER.setLevel(logging.INFO)
_HANDLER.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add file handler to the logger.
LOGGER.addHandler(_HANDLER)

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
