from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import time
from api.utils.telegram_auth import (
    validate_telegram_data,
    validate_telegram_login,
    get_user_from_init_data,
    create_access_token,
    TelegramUser
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/telegram-tma")
async def login_tma(init_data: str = Body(..., embed=True)) -> dict:
    if not validate_telegram_data(init_data):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram Data")

    user_dict = get_user_from_init_data(init_data)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Bad Request: Missing or invalid user data")

    # In TMA, auth_date is a top level param in init_data, but let's parse it if present.
    # Actually, validate_telegram_data uses unquote, we can find auth_date similarly
    from urllib.parse import unquote
    parsed_data = dict(chunk.split("=", 1) for chunk in unquote(init_data).split("&"))
    if "auth_date" in parsed_data:
        if time.time() - int(parsed_data["auth_date"]) > 86400: # 24 hours
             raise HTTPException(status_code=401, detail="Auth data is expired")

    user = TelegramUser(**user_dict)
    token = create_access_token(user.model_dump())
    return {"access_token": token, "token_type": "bearer"}

@router.post("/telegram-tgl")
async def login_tgl(login_data: Dict[str, Any] = Body(...)) -> dict:
    if not validate_telegram_login(login_data.copy()):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Telegram Login Data")

    if "auth_date" in login_data:
        if time.time() - int(login_data["auth_date"]) > 86400:
            raise HTTPException(status_code=401, detail="Auth data is expired")

    user = TelegramUser(**login_data)
    token = create_access_token(user.model_dump())
    return {"access_token": token, "token_type": "bearer"}
