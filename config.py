"""
This module contains configuration settings for the Money Manager application.
"""

import os

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", None)
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")

TOKEN_SECRET_KEY = os.getenv("TOKEN_SECRET_KEY")
TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM")

API_BIND_HOST = os.getenv("API_BIND_HOST", "0.0.0.0")
API_BIND_PORT = int(os.getenv("API_BIND_PORT", "9999"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", None)
TELEGRAM_BOT_API_BASE_URL = os.getenv(
    "TELEGRAM_BOT_API_BASE_URL", "http://localhost:9999"
)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
