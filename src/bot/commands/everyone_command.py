import random
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.logger_base import logger
from decorators.cooldown import cooldown
from decorators.set_sentry_context import set_sentry_context
from decorators.is_group import is_group
from services.user_service import UserService
from services.group_service import GroupService
from services.log_service import LogService
from utils.session_manager import Session
from utils.config import settings


@set_sentry_context
@cooldown(15)
@is_group
async def everyoneMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    try:
        group_id = update.message.chat.id
        data = GroupService.get_users_in_group(session, str(group_id))

        random_number = random.randint(0, 5)
        donation_text = (
            "\n\nEnjoying this free bot? 🌟 Show your support by making a donation to help keep it running and improving! Every contribution matters. 🙏 Donate here: https://github.com/Matt0550/TagEveryoneTelegramBot#support-me"
            if random_number == 5
            else ""
        )

        if not data:
            await update.message.reply_text("No one is in the list")
        else:
            try:
                mentions = []
                for user in data:
                    try:
                        member = await update.message.chat.get_member(user.user_id)
                        if member.user.username is not None:
                            UserService.update_user(
                                session, user.user_id, username=member.user.username
                            )
                        username = (
                            member.user.username
                            if member.user.username is not None
                            else user.username
                        )
                    except Exception as e:
                        username = None
                        error_message_lower = str(e).lower()
                        if (
                            "member not found" in error_message_lower
                            or "participant_id_invalid" in error_message_lower
                        ):
                            GroupService.remove_user_from_group(
                                session, str(group_id), user.user_id
                            )
                            continue
                        continue

                    if user.user_id == update.effective_user.id:
                        mentions.append("You")
                    elif username is not None:
                        mentions.append(
                            f"<a href='tg://user?id={user.user_id}'>@{username}</a>"
                        )
                    elif user.first_name is not None:
                        text = f"{user.first_name}"
                        if user.last_name is not None:
                            text += f" {user.last_name}"
                        mentions.append(
                            f"<a href='tg://user?id={user.user_id}'>{text}</a>"
                        )
                    else:
                        mentions.append(
                            f"<a href='tg://user?id={user.user_id}'>{user.user_id}</a>"
                        )

                batch_size = 50
                for i in range(0, len(mentions), batch_size):
                    batch = mentions[i : i + batch_size]
                    user_mentions = "\n".join(batch)
                    if user_mentions:
                        await update.message.reply_text(
                            user_mentions + donation_text,
                            disable_web_page_preview=True,
                            parse_mode=ParseMode.HTML,
                        )

                LogService.add_log(
                    session,
                    update.message.from_user.id,
                    str(group_id),
                    "everyone",
                    "Message sent to all in the list",
                )
            except Exception as e:
                logger.error(f"[ERROR] {e}")
                await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
                LogService.add_log(
                    session, update.message.from_user.id, str(group_id), "error", str(e)
                )
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
    finally:
        Session.remove()


@set_sentry_context
async def everyone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.edited_message is not None or update.message is None:
            return
        if update.message.text is not None:
            if any(
                comm.lower() in update.message.text.lower()
                for comm in settings.EVERYONE_COMMANDS
            ) or any(
                comm in update.message.text for comm in settings.EVERYONE_COMMANDS
            ):
                await everyoneMessage(update, context)
    except Exception as e:
        logger.error(f"[ERROR] {e}")
