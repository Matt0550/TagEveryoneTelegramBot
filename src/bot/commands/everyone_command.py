import json
import random
import string

from sqlmodel import select
from telegram import ReactionTypeEmoji, Update
from telegram.constants import ParseMode, ReactionEmoji
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from celery_workers.tasks.send_telegram_message import send_telegram_message
from models_all.tag_list import TagList
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.log_service import LogService
from services.mention_service import MentionService
from utils.logger_base import logger
from utils.session_manager import Session, engine


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
                # Set a reaction to acknowledge the command
                try:
                    await update.message.set_reaction(
                        reaction=ReactionTypeEmoji(ReactionEmoji.THUMBS_UP)
                    )
                except Exception as reaction_error:
                    logger.warning(f"Could not set reaction: {reaction_error}")

                # Build mention strings with cached usernames
                mentions = await MentionService.build_mentions(
                    session=session,
                    group_id=group.id,
                    group_telegram_id=group.telegram_id,
                    user_ids=user_ids,
                    exclude_user_id=update.effective_user.id,
                    update=update,
                )

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
