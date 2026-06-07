import hashlib
import hmac
import json
from urllib.parse import unquote

from telegram import Bot
from telegram.error import TelegramError

from utils.config import settings


async def check_telegram_admin(chat_id: int, user_id: int, bot: Bot | None = None) -> bool:
    bot_instance = bot or Bot(token=settings.BOT_TOKEN)
    try:
        member = await bot_instance.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except TelegramError:
        return False


async def check_telegram_member(chat_id: int, user_id: int, bot: Bot | None = None) -> bool:
    bot_instance = bot or Bot(token=settings.BOT_TOKEN)
    try:
        member = await bot_instance.get_chat_member(chat_id, user_id)
        return member.status not in ["left", "kicked", "banned"]
    except TelegramError:
        return False


def validate_telegram_data(init_data: str, c_str: str = "WebAppData") -> bool:
    """
    Validates the data received from the Telegram web app using HMAC.
    """
    try:
        parsed_data = dict(
            chunk.split("=", 1) for chunk in unquote(init_data).split("&")
        )
        if "hash" not in parsed_data:
            return False

        hash_str = parsed_data.pop("hash")

        sorted_data = sorted(parsed_data.items(), key=lambda x: x[0])
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_data])

        secret_key = hmac.new(
            c_str.encode(), settings.BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        data_check = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)

        return data_check.hexdigest() == hash_str
    except Exception:
        return False


def validate_telegram_login(data: dict) -> bool:
    """
    Validates data received from the Telegram Login Widget.
    Uses the SHA256 hash of the BOT_TOKEN as the secret key.
    """
    try:
        if "hash" not in data:
            return False

        hash_str = data.pop("hash")

        # Convert all values to strings for sorting and joining
        sorted_data = sorted(data.items(), key=lambda x: x[0])
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_data])

        secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
        data_check = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)

        return data_check.hexdigest() == hash_str
    except Exception:
        return False


def get_user_from_init_data(init_data: str) -> dict | None:
    """
    Extracts the user dictionary from the init_data string safely.
    """
    try:
        parsed_data = dict(
            chunk.split("=", 1) for chunk in unquote(init_data).split("&")
        )
        user_str = unquote(parsed_data.get("user", ""))

        # Parse the JSON string into a dictionary
        user = json.loads(user_str)
        return user if isinstance(user, dict) else None
    except Exception:
        return None
