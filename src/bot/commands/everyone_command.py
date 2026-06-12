import json
import string

from telegram import ReactionTypeEmoji, Update
from telegram.constants import ReactionEmoji
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.utils.errors import reply_generic_error
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.list_service import ListService
from services.log_service import LogService
from utils.logger_base import logger
from utils.session_manager import Session, engine


async def triggerMessage(
    update: Update, _context: ContextTypes.DEFAULT_TYPE, matched_lists: list, group
):
    session = Session(engine)
    try:
        list_repo = ListRepository()
        list_user_repo = ListUserRepository()
        group_repo = GroupRepository()
        list_service = ListService(
            session=session,
            repository=list_repo,
            user_repo=list_user_repo,
            group_repo=group_repo,
        )

        try:
            # Set a reaction to acknowledge the command
            try:
                await update.message.set_reaction(
                    reaction=ReactionTypeEmoji(ReactionEmoji.THUMBS_UP)
                )
            except Exception as reaction_error:
                logger.warning(f"Could not set reaction: {reaction_error}")

            reply_to_id = update.message.message_id
            if update.message.reply_to_message:
                reply_to_id = update.message.reply_to_message.message_id

            list_ids = [tag_list.id for tag_list in matched_lists]

            await list_service.trigger_multiple_lists_by_command(
                triggering_user_id=update.effective_user.id,
                group_id=group.id,
                list_ids=list_ids,
                bot=None,
                update=update,
                reply_to_message_id=reply_to_id,
            )

        except Exception as e:
            logger.exception(f"[ERROR] triggerMessage inner: {e}")
            await reply_generic_error(update, _context)
            LogService.add_log(
                session, update.message.from_user.id, group.id, "error", str(e)
            )
    except Exception as e:
        logger.exception(f"[ERROR] triggerMessage outer: {e}")
        await reply_generic_error(update)
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
                list_repo = ListRepository()
                group_repo = GroupRepository()
                list_user_repo = ListUserRepository()
                group = group_repo.get_by_telegram_id(session, update.message.chat.id)
                if not group:
                    return

                list_service = ListService(
                    session=session,
                    repository=list_repo,
                    user_repo=list_user_repo,
                    group_repo=group_repo,
                )
                all_lists = list_service.get_active_lists(group.id)

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
