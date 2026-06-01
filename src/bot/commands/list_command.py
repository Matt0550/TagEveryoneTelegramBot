from telegram import Update
from telegram.ext import ContextTypes
from utils.logger_base import logger
from decorators.cooldown import cooldown
from decorators.set_sentry_context import set_sentry_context
from services.group_service import GroupService
from services.log_service import LogService
from utils.session_manager import Session


@set_sentry_context
@cooldown(15)
async def getList(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    try:
        group_id = update.message.chat.id
        data = GroupService.get_users_in_group(session, str(group_id))

        if not data:
            await update.message.reply_text("No one is in the list")
        else:
            try:
                members = []
                for user in data:
                    try:
                        member = await update.message.chat.get_member(user.user_id)
                        username = (
                            member.user.username
                            if member.user.username is not None
                            else member.user.full_name
                        )
                        members.append(username)
                    except Exception as e:
                        error_message_lower = str(e).lower()
                        if (
                            "member not found" in error_message_lower
                            or "participant_id_invalid" in error_message_lower
                        ):
                            GroupService.remove_user_from_group(
                                session, str(group_id), user.user_id
                            )
                        continue

                await update.message.reply_text(
                    "\n".join(members)
                    + "\n\nThanks for using this bot. Buy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot",
                    disable_web_page_preview=True,
                )

                LogService.add_log(
                    session,
                    update.message.from_user.id,
                    str(group_id),
                    "list",
                    "List sent",
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
