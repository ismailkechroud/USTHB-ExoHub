# Library (default)
import os

# Library (.venv)
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

load_dotenv()





# Bot Tokens
USER_BOT_TOKEN = os.getenv("USER_BOT_TOKEN")
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")


# Telegram IDs
CHANNEL_ID = os.getenv("CHANNEL_ID")



# Bots
user_bot = Bot(
    token=USER_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
admin_bot = Bot(
    token=ADMIN_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)