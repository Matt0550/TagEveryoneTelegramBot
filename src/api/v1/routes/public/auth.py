import time
from typing import Any
from urllib.parse import unquote

from fastapi import APIRouter, Body

from api.utils.telegram_auth import (
    TelegramUser,
    create_access_token,
)
from api.utils.telegram_utils import (
    get_user_from_init_data,
    validate_telegram_data,
    validate_telegram_login,
)
from models_all.enums import Role
from models_all.exceptions import BadRequestException, UnauthorizedException
from utils.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/telegram-tma")
async def login_tma(init_data: str = Body(..., embed=True)) -> dict:
    if not validate_telegram_data(init_data):
        raise UnauthorizedException("Unauthorized: Invalid Telegram Data")

    user_dict = get_user_from_init_data(init_data)
    if not user_dict:
        raise BadRequestException("Bad Request: Missing or invalid user data")

    parsed_data = dict(chunk.split("=", 1) for chunk in unquote(init_data).split("&"))
    if "auth_date" in parsed_data:
        if time.time() - int(parsed_data["auth_date"]) > 86400:  # 24 hours
            raise UnauthorizedException("Auth data is expired")

    user = TelegramUser(**user_dict)

    role = Role.SUPER_ADMIN if str(user.id) == str(settings.OWNER_ID) else Role.USER

    payload = user.model_dump()
    payload["role"] = role
    token = create_access_token(payload)

    return {"access_token": token, "token_type": "bearer", "user": user.model_dump(), "role": role}

@router.post("/telegram-tgl")
async def login_tgl(login_data: dict[str, Any] = Body(...)) -> dict:
    if not validate_telegram_login(login_data.copy()):
        raise UnauthorizedException("Unauthorized: Invalid Telegram Login Data")

    if "auth_date" in login_data:
        if time.time() - int(login_data["auth_date"]) > 86400:
            raise UnauthorizedException("Auth data is expired")

    user = TelegramUser(**login_data)

    role = Role.SUPER_ADMIN if str(user.id) == str(settings.OWNER_ID) else Role.USER

    payload = user.model_dump()
    payload["role"] = role
    token = create_access_token(payload)

    return {"access_token": token, "token_type": "bearer", "user": user.model_dump(), "role": role}
