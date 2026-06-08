import uuid

from fastapi import Depends, Request
from sqlmodel import Session
from telegram import Bot

from api.dependencies import get_session
from api.utils.telegram_auth import TelegramUser, verify_telegram_webapp
from api.utils.telegram_utils import check_telegram_admin
from models_all.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from models_all.group import Group
from models_all.tag_list import TagList
from repositories.group_admin_exclusion_repository import GroupAdminExclusionRepository
from utils.config import settings


def get_current_user(
    user: TelegramUser = Depends(verify_telegram_webapp),
) -> TelegramUser:
    return user


def require_super_admin(user: TelegramUser = Depends(get_current_user)) -> TelegramUser:
    if str(user.id) != str(settings.OWNER_ID):
        raise ForbiddenException("SuperAdmin privileges required")
    return user


async def is_group_admin(group: Group, user: TelegramUser, db: Session, bot: Bot | None = None) -> bool:
    # SuperAdmin always has access
    if str(user.id) == str(settings.OWNER_ID):
        return True

    # Check database exclusion list
    repo = GroupAdminExclusionRepository()
    if repo.is_excluded(db, group.id, user.id):
        return False

    # Verify admin status via Telegram
    return await check_telegram_admin(group.telegram_id, user.id, bot=bot)


async def require_group_admin(
    request: Request,
    user: TelegramUser = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> TelegramUser:
    group_id_str = request.path_params.get("group_id")
    if not group_id_str:
        raise BadRequestException("group_id path parameter is required")

    try:
        internal_group_id = uuid.UUID(group_id_str)
    except ValueError:
        raise BadRequestException("Invalid group_id format")

    group = db.get(Group, internal_group_id)
    if not group:
        raise NotFoundException("Group not found")

    if not await is_group_admin(group, user, db):
        raise ForbiddenException("GroupAdmin privileges required")

    return user


def require_list_in_group(
    request: Request,
    db: Session = Depends(get_session),
) -> None:
    """FastAPI dependency: assert that ``list_id`` belongs to ``group_id``.

    Pair this with ``require_group_admin`` on any ``/groups/{group_id}/lists/{list_id}/...``
    route to prevent admins of one group from operating on another group's lists
    via mismatched path parameters.

    :raises BadRequestException: if either path parameter is malformed.
    :raises NotFoundException: if the list is missing, inactive, or in another group.
    """
    group_id_str = request.path_params.get("group_id")
    list_id_str = request.path_params.get("list_id")
    if not group_id_str or not list_id_str:
        raise BadRequestException("group_id and list_id path parameters are required")
    try:
        group_uuid = uuid.UUID(group_id_str)
        list_uuid = uuid.UUID(list_id_str)
    except ValueError:
        raise BadRequestException("Invalid group_id or list_id format")

    tag_list = db.get(TagList, list_uuid)
    if not tag_list or not tag_list.active or tag_list.group_id != group_uuid:
        raise NotFoundException("List not found")
