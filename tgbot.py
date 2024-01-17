import traceback

import telebot
from telebot.apihelper import requests
from telebot.apihelper import ApiTelegramException

from config import BOT_TOKEN, CHANNEL_ID, TIMEOUT
from logger import print_and_log

BOT = telebot.TeleBot(BOT_TOKEN)
telebot.apihelper.proxy = None

def send_message(text, user=CHANNEL_ID):
    # Attempt to send the message 5 times.
    for _ in range(5):
        try:
            # Try sending the message using the Telegram Bot
            BOT.send_message(user, text, parse_mode="Markdown", timeout=TIMEOUT, disable_web_page_preview=True)
        except (requests.exceptions.SSLError, requests.exceptions.ProxyError, requests.exceptions.ReadTimeout, ApiTelegramException) as e:
            # Handle specific exceptions related to network issues or rate limiting.
            exception = str(e)
            
            if "429" in exception:
                # If rate limited, sleep for 30 seconds before retrying.
                print_and_log("Rate limit exceeded. Waiting for 30 seconds before retrying...", level="info")
                from main import _sleep
                _sleep(30)

            continue
        except:
            # If the message fails to send due to other reasons, log the exception and give up on sending.
            for line in traceback.format_exc().splitlines():
                print_and_log(line, level="warning")
            print_and_log("Failed to post message to Telegram!", level="warning")
            return
        else:
            # Successfully sent the message, exit the loop.
            return
    
    # If all 5 attempts fail, log a warning message.
    print_and_log("Failed to post message to Telegram even after many attempts!", level="warning")