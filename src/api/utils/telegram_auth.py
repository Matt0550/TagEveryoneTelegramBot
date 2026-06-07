from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from models_all.exceptions import ForbiddenException, UnauthorizedException
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


async def verify_telegram_webapp(
    authorization: str = Depends(api_key_header),
) -> TelegramUser:
    """
    FastAPI dependency to verify the JWT authentication token.
    Expects 'Authorization: Bearer <token>'
    """
    if not authorization:
        raise UnauthorizedException("Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(
            "Invalid authorization header format. Expected 'Bearer <token>'"
        )

    token = authorization[7:]
    secret = settings.SECRET_KEY or settings.BOT_TOKEN

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return TelegramUser(**payload)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid token")


async def verify_admin(
    user: TelegramUser = Depends(verify_telegram_webapp),
) -> TelegramUser:
    """
    FastAPI dependency to verify if the user is an admin.
    """
    if str(user.id) != str(settings.OWNER_ID):
        raise ForbiddenException("Forbidden: You are not an admin")

    return user
