from datetime import UTC, datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from models_all.group import GroupCreate
from models_all.user import UserCreate
from services.group_service import GroupService
from services.user_service import UserService
from utils.logger_base import logger
from utils.session_manager import Session, engine


async def activity_middleware(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Middleware to check and update user/group last activity.
    If updated_at is older than 24h, updates the basic information.
    Reactivates inactive users upon new activity.
    """
    if not update:
        return

    session = Session(engine)
    try:
        user = update.effective_user
        chat = update.effective_chat

        if user and not user.is_bot:
            db_user = UserService.get_or_create_user(
                session,
                UserCreate(
                    user_id=user.id,
                    username=getattr(user, "username", None),
                    first_name=getattr(user, "first_name", None),
                    last_name=getattr(user, "last_name", None),
                ),
            )

            needs_update = False

            if not db_user.active:
                db_user.active = True
                db_user.deleted_at = None
                needs_update = True
                logger.info(f"Reactivated user {user.id} due to new activity.")

            if db_user.updated_at:
                user_updated_at = db_user.updated_at.replace(tzinfo=UTC) if db_user.updated_at.tzinfo is None else db_user.updated_at
                if datetime.now(UTC) - user_updated_at > timedelta(hours=24):
                    db_user.username = getattr(user, "username", None)
                    db_user.first_name = getattr(user, "first_name", None)
                    db_user.last_name = getattr(user, "last_name", None)
                    db_user.updated_at = datetime.now(UTC)
                    needs_update = True
            else:
                db_user.updated_at = datetime.now(UTC)
                needs_update = True

            if needs_update:
                session.add(db_user)

        if chat and chat.type in ["group", "supergroup"]:
            try:
                members_count = await chat.get_member_count()
            except Exception:
                members_count = None

            db_group = GroupService.get_or_create_group(
                session,
                GroupCreate(
                    telegram_id=chat.id,
                    group_name=getattr(chat, "title", None),
                    group_description=getattr(chat, "description", None),
                    group_username=getattr(chat, "username", None),
                    group_type=getattr(chat, "type", None),
                    group_members=members_count,
                ),
            )

            needs_update = False
            if db_group.updated_at:
                group_updated_at = db_group.updated_at.replace(tzinfo=UTC) if db_group.updated_at.tzinfo is None else db_group.updated_at
                if datetime.now(UTC) - group_updated_at > timedelta(hours=24):
                    db_group.group_name = getattr(chat, "title", None)
                    db_group.group_description = getattr(chat, "description", None)
                    db_group.group_username = getattr(chat, "username", None)
                    db_group.group_type = getattr(chat, "type", None)
                    if members_count is not None:
                        db_group.group_members = members_count
                    db_group.updated_at = datetime.now(UTC)
                    needs_update = True
            else:
                db_group.updated_at = datetime.now(UTC)
                needs_update = True

            if needs_update:
                session.add(db_group)

        session.commit()
    except Exception as e:
        logger.error(f"[ERROR in activity_middleware] {e}")
    finally:
        session.close()
