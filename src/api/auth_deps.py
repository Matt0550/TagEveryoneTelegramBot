
from fastapi import Depends, HTTPException, Request
from sqlmodel import Session
from telegram import Bot
from telegram.error import TelegramError

from api.dependencies import get_session
from api.utils.telegram_auth import TelegramUser, verify_telegram_webapp
from repositories.group_admin_exclusion_repository import GroupAdminExclusionRepository
from utils.config import settings


async def check_telegram_admin(chat_id: int, user_id: int) -> bool:
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except TelegramError:
        return False

def get_current_user(user: TelegramUser = Depends(verify_telegram_webapp)) -> TelegramUser:
    return user

def require_super_admin(user: TelegramUser = Depends(get_current_user)) -> TelegramUser:
    if str(user.id) != str(settings.OWNER_ID):
        raise HTTPException(status_code=403, detail="SuperAdmin privileges required")
    return user

from models_all.group import Group


async def is_group_admin(
    group: Group,
    user: TelegramUser,
    db: Session
) -> bool:
    # SuperAdmin always has access
    if str(user.id) == str(settings.OWNER_ID):
        return True

    # Check database exclusion list
    repo = GroupAdminExclusionRepository()
    if repo.is_excluded(db, group.id, user.id):
        return False

    # Verify admin status via Telegram
    return await check_telegram_admin(group.telegram_id, user.id)

async def require_group_admin(
    request: Request,
    user: TelegramUser = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> TelegramUser:
    group_id_str = request.path_params.get("group_id")
    if not group_id_str:
        raise HTTPException(status_code=400, detail="group_id path parameter is required")

    import uuid
    try:
        internal_group_id = uuid.UUID(group_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid group_id format")

    from models_all.group import Group
    group = db.get(Group, internal_group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if not await is_group_admin(group, user, db):
        raise HTTPException(status_code=403, detail="GroupAdmin privileges required")

    return user
