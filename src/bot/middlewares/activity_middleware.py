from datetime import UTC, datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from bot.i18n import resolve_group_locale
from models_all.group import GroupCreate
from models_all.user import UserCreate
from services.group_service import GroupService
from services.user_service import UserService
from utils.languages import normalize_language
from utils.logger_base import logger
from utils.session_manager import Session, engine


async def activity_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Middleware to check and update user/group last activity.
    If updated_at is older than 24h, updates the basic information.
    Reactivates inactive users upon new activity.

    Also caches the per-update reply locale in ``context.chat_data["locale"]``
    so command handlers and decorators can translate responses without an extra
    settings query. Refreshed every update, so a language change applies at once.
    """
    if not update:
        return

    session = Session(engine)
    db_group = None
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

        # Cache the reply locale for this update (resolved while the session is
        # open so group.settings can lazy-load). Group setting wins; otherwise
        # fall back to the Telegram user's client language.
        chat_data = getattr(context, "chat_data", None)
        if isinstance(chat_data, dict):
            if db_group is not None:
                chat_data["locale"] = resolve_group_locale(db_group)
            else:
                lang = getattr(user, "language_code", None) if user else None
                chat_data["locale"] = normalize_language(lang)

        session.commit()
    except Exception as e:
        logger.error(f"[ERROR in activity_middleware] {e}")
    finally:
        session.close()
