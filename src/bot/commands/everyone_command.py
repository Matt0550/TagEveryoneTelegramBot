import json
import random
import string
from datetime import UTC, datetime, timedelta

from sqlmodel import select
from telegram import ReactionTypeEmoji, Update
from telegram.constants import ParseMode, ReactionEmoji
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from celery_workers.tasks.send_telegram_message import send_telegram_message
from models_all.tag_list import TagList
from models_all.user import UserCreate
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from repositories.user_repository import UserRepository
from services.group_service import GroupService
from services.log_service import LogService
from services.user_service import UserService
from utils.logger_base import logger
from utils.session_manager import Session, engine

# Users with updated_at older than this will be re-fetched from Telegram
USER_CACHE_MAX_AGE = timedelta(hours=24)


async def _resolve_username(
    update: Update,
    session: Session,
    user_service: UserService,
    group_service: GroupService,
    group,
    uid: int,
) -> str | None:
    """
    Resolve a user's username, using the DB cache when fresh enough.

    If the cached user is stale (updated_at > 24h) or missing, performs a
    Telegram API lookup and updates the DB.

    Returns the username string, or None if the user can't be resolved.
    Returns "SKIP" if the user left the group and was removed.
    """
    db_user = user_service.get_by_id(uid)

    # Check if cached data is fresh enough
    if db_user and db_user.username:
        cache_cutoff = datetime.now(UTC) - USER_CACHE_MAX_AGE
        if db_user.updated_at:
            updated_at_aware = db_user.updated_at.replace(tzinfo=UTC) if db_user.updated_at.tzinfo is None else db_user.updated_at
            if updated_at_aware >= cache_cutoff:
                return db_user.username
        elif db_user.created_at:
            created_at_aware = db_user.created_at.replace(tzinfo=UTC) if db_user.created_at.tzinfo is None else db_user.created_at
            if created_at_aware >= cache_cutoff:
                return db_user.username

    # Cache is stale or user not in DB — perform live lookup
    try:
        member = await update.message.chat.get_member(uid)
        if member.user.username is not None:
            user_service.get_or_create_user(
                session,
                UserCreate(
                    user_id=uid,
                    username=member.user.username,
                    first_name=member.user.first_name,
                    last_name=member.user.last_name,
                ),
            )
        return member.user.username
    except Exception as e:
        error_message_lower = str(e).lower()
        if (
            "member not found" in error_message_lower
            or "participant_id_invalid" in error_message_lower
            or "user not found" in error_message_lower
        ):
            group_service.remove_user_from_group(group.id, uid)
            return "SKIP"

        # Fallback to DB cache even if stale
        if db_user:
            return db_user.username
        return None


async def triggerMessage(
    update: Update, _context: ContextTypes.DEFAULT_TYPE, matched_lists: list, group
):
    session = Session(engine)
    try:
        list_user_repo = ListUserRepository()

        # Collect unique user_ids from all matched lists
        user_ids = set()
        list_names = []
        for tag_list in matched_lists:
            list_names.append(tag_list.name)
            users = list_user_repo.get_users_in_list(session, tag_list.id)
            for u in users:
                user_ids.add(u.user_id)

        random_number = random.randint(0, 5)
        donation_text = (
            "\n\nEnjoying this free bot? 🌟 Show your support by making a donation to help keep it running and improving! Every contribution matters. 🙏 Donate here: https://github.com/Matt0550/TagEveryoneTelegramBot#support-me"
            if random_number == 5
            else ""
        )

        if not user_ids:
            await update.message.reply_text("No one is in the list")
        else:
            try:
                user_service = UserService(session, UserRepository())
                group_service = GroupService(session, GroupRepository())

                # Set a reaction to acknowledge the command
                try:
                    await update.message.set_reaction(
                        reaction=ReactionTypeEmoji(ReactionEmoji.THUMBS_UP)
                    )
                except Exception as reaction_error:
                    logger.warning(f"Could not set reaction: {reaction_error}")

                # Build mention strings with cached usernames
                mentions = []
                for uid in user_ids:
                    if uid == update.effective_user.id:
                        mentions.append("You")
                        continue

                    username = await _resolve_username(
                        update, session, user_service, group_service, group, uid
                    )

                    if username == "SKIP":
                        continue
                    elif username is not None:
                        mentions.append(f"<a href='tg://user?id={uid}'>@{username}</a>")
                    else:
                        mentions.append(f"<a href='tg://user?id={uid}'>👤</a>")

                # Determine which message to reply to
                reply_to_id = update.message.message_id
                if update.message.reply_to_message:
                    reply_to_id = update.message.reply_to_message.message_id

                # Dispatch each batch as a Celery task
                chat_id = update.message.chat.id
                batch_size = 50
                for i in range(0, len(mentions), batch_size):
                    batch = mentions[i : i + batch_size]
                    user_mentions = "\n".join(batch)
                    if user_mentions:
                        message_text = user_mentions + donation_text
                        send_telegram_message.delay(
                            chat_id=chat_id,
                            text=message_text,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_to_message_id=reply_to_id,
                        )

                LogService.add_log(
                    session,
                    update.message.from_user.id,
                    group.id,
                    "trigger_list",
                    f"Message dispatched to lists: {', '.join(list_names)} "
                    f"({len(mentions)} users, async)",
                )
            except Exception as e:
                logger.error(f"[ERROR] {e}")
                await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
                LogService.add_log(
                    session, update.message.from_user.id, group.id, "error", str(e)
                )
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
    finally:
        session.close()


@cooldown(15)
@is_group
async def everyone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.edited_message is not None or update.message is None:
            return
        if update.message.text is not None:
            text = update.message.text.lower()
            words = text.split()

            triggers = []
            for w in words:
                if w.startswith("@") or w.startswith("/"):
                    trigger = w[1:]
                    trigger = trigger.rstrip(string.punctuation)
                    trigger = trigger.split("@")[0]
                    triggers.append(trigger)

            if not triggers:
                return

            session = Session(engine)
            try:
                ListRepository()
                group_repo = GroupRepository()
                group = group_repo.get_by_telegram_id(session, update.message.chat.id)
                if not group:
                    return

                # Get all lists for this group

                statement = select(TagList).where(
                    TagList.group_id == group.id, TagList.active == True
                )
                all_lists = session.exec(statement).all()

                matched_lists = []
                for tag_list in all_lists:
                    # Check trigger name
                    if tag_list.trigger_name.lower() in triggers:
                        matched_lists.append(tag_list)
                    # Check aliases if implemented
                    elif tag_list.aliases:
                        aliases = tag_list.aliases
                        if isinstance(aliases, str):
                            try:
                                aliases = json.loads(aliases)
                            except Exception:
                                aliases = []

                        if any(a.lower() in triggers for a in aliases):
                            matched_lists.append(tag_list)

                if matched_lists:
                    await triggerMessage(update, context, matched_lists, group)
            finally:
                session.close()
    except Exception as e:
        logger.error(f"[ERROR] {e}")
