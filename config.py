import os

# Log file name
LOG_FILE = "log.txt"

# Enable multi-threading mode.
ENABLE_MULTI_THREAD = True

# Number of threads to use in multi-threading mode. (default: 4, recommended not to exceed 8)
MAX_THREADS_NUM = 8

# Enable logging.
ENABLE_LOGGER = True

# When LESS_LOG is True, the log file will no longer write records with no updates.
LESS_LOG = False

# Loop check interval (unit: seconds) (default: 5 minutes)
LOOP_CHECK_INTERVAL = 5 * 60

# Request timeout
TIMEOUT = 30

# Enable the feature to send messages using the Telegram bot.
ENABLE_SENDMESSAGE = True

# Telegram bot token
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

# ID of the channel to send updates to
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# GitHub username
GH_USERNAME = str(os.getenv("GH_USERNAME"))

# GitHub token
GH_TOKEN = str(os.getenv("GH_TOKEN"))

# Dropbox access token
DROPBOX_ACCESS_TOKEN = str(os.getenv("DROPBOX_ACCESS_TOKEN"))