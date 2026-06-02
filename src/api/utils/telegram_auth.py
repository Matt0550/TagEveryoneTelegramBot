import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from urllib.parse import unquote

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from utils.config import settings


class TelegramUser(BaseModel):
    id: int
    is_bot: bool | None = None
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None
    added_to_attachment_menu: bool | None = None
    allows_write_to_pm: bool | None = None
    photo_url: str | None = None


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


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"exp": expire})
    secret = settings.SECRET_KEY or settings.BOT_TOKEN
    encoded_jwt = jwt.encode(to_encode, secret, algorithm="HS256")
    return encoded_jwt

api_key_header = APIKeyHeader(
    name="Authorization",
    auto_error=False,
    description="Authorization header containing Bearer <jwt_token>",
)


async def verify_telegram_webapp(authorization: str = Depends(api_key_header)) -> TelegramUser:
    """
    FastAPI dependency to verify the JWT authentication token.
    Expects 'Authorization: Bearer <token>'
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
        )

    token = authorization[7:]
    secret = settings.SECRET_KEY or settings.BOT_TOKEN

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return TelegramUser(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def verify_admin(user: TelegramUser = Depends(verify_telegram_webapp)) -> TelegramUser:
    """
    FastAPI dependency to verify if the user is an admin.
    """
    if str(user.id) != str(settings.OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: You are not an admin")

    return user
