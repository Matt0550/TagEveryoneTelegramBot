from datetime import UTC, datetime

from sqlmodel import select
from telegram import Update
from telegram.ext import ContextTypes

from models_all.group import GroupCreate
from models_all.list_user import ListUser
from models_all.tag_list import TagList
from models_all.user import UserCreate
from repositories.list_user_repository import ListUserRepository
from services.group_service import GroupService
from services.user_service import UserService
from utils.logger_base import logger
from utils.session_manager import Session, engine


async def my_chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles events where the bot's status in a chat changes
    (e.g. bot is added to a group, promoted, or kicked).
    """
    if not update.my_chat_member:
        return

    session = Session(engine)
    try:
        new_status = update.my_chat_member.new_chat_member.status
        chat = update.my_chat_member.chat

        if chat.type in ["group", "supergroup"]:
            if new_status in ["member", "administrator"]:
                logger.info(f"Bot added to group {chat.id} with status {new_status}")

                try:
                    members_count = await chat.get_member_count()
                except Exception:
                    members_count = 0

                GroupService.get_or_create_group(
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

                if new_status == "member":
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text="👋 Hello! Thanks for adding me. Please promote me to Administrator so I can function properly.",
                    )

            elif new_status in ["left", "kicked"]:
                logger.info(f"Bot removed from group {chat.id}")

    except Exception as e:
        logger.error(f"[ERROR in my_chat_member_handler] {e}")
    finally:
        session.close()


async def chat_member_handler(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Handles events where another user joins or leaves a chat.
    Requires bot to be admin and/or privacy mode disabled.
    """
    if not update.chat_member:
        return

    session = Session(engine)
    try:
        chat = update.chat_member.chat
        if chat.type not in ["group", "supergroup"]:
            return

        new_status = update.chat_member.new_chat_member.status
        user = update.chat_member.new_chat_member.user

        if user.is_bot:
            return

        db_user = UserService.get_or_create_user(
            session,
            UserCreate(
                user_id=user.id,
                username=getattr(user, "username", None),
                first_name=getattr(user, "first_name", None),
                last_name=getattr(user, "last_name", None),
            ),
        )

        db_group = GroupService.get_or_create_group(
            session,
            GroupCreate(
                telegram_id=chat.id,
                group_name=getattr(chat, "title", None),
                group_description=getattr(chat, "description", None),
                group_username=getattr(chat, "username", None),
                group_type=getattr(chat, "type", None),
            ),
        )

        list_user_repo = ListUserRepository()

        if new_status in ["member", "administrator", "creator"]:
            if (
                db_group.settings
                and db_group.settings.auto_add_new_members
                and db_group.settings.auto_add_lists
            ):
                for list_to_add in db_group.settings.auto_add_lists:
                    existing = list_user_repo.get_subscription(
                        session, list_to_add.id, user.id
                    )
                    if not existing:
                        list_user_repo.create(
                            session,
                            ListUser(
                                list_id=list_to_add.id, user_id=user.id
                            ),
                        )
                        logger.info(
                            f"Auto-added user {user.id} to list {list_to_add.id}"
                        )

        elif new_status in ["left", "kicked"]:
            query = (
                select(ListUser)
                .join(TagList)
                .where(ListUser.user_id == user.id)
                .where(TagList.group_id == db_group.id)
                .where(ListUser.active == True)
            )
            subscriptions = session.exec(query).all()

            for sub in subscriptions:
                sub.active = False
                sub.deleted_at = datetime.now(UTC)
                session.add(sub)

            session.commit()

            active_subs_query = select(ListUser).where(
                ListUser.user_id == user.id, ListUser.active == True
            )
            active_subs = session.exec(active_subs_query).first()
            if not active_subs:
                db_user.active = False
                session.add(db_user)
                session.commit()
                logger.info(
                    f"User {user.id} deactivated because they have no more active lists."
                )

    except Exception as e:
        logger.error(f"[ERROR in chat_member_handler] {e}")
    finally:
        session.close()
