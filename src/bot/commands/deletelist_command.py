from decorators.cooldown import cooldown
from decorators.is_group import is_group
from decorators.require_admin import require_admin
from decorators.set_sentry_context import set_sentry_context
from telegram import Update
from telegram.ext import ContextTypes

from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from services.log_service import LogService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@set_sentry_context
@cooldown(5)
@is_group
@require_admin
async def deletelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        args = context.args

        if not args:
            await update.message.reply_text("Usage: /deletelist <trigger_name>")
            return

        trigger_name = args[0].lower()
        if trigger_name.startswith('@') or trigger_name.startswith('/'):
            trigger_name = trigger_name[1:]

        group_repo = GroupRepository()
        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text("Group not registered.")
            return

        list_repo = ListRepository()
        target_list = list_repo.get_by_trigger_name(session, group.id, trigger_name)

        if not target_list:
            await update.message.reply_text(f"List '{trigger_name}' not found.")
            return

        if target_list.is_system:
            await update.message.reply_text("You cannot delete a system list.")
            return

        list_repo.delete(session, target_list.id)

        await update.message.reply_text(f"List '{target_list.name}' deleted successfully!")
        LogService.add_log(session, user_id, group.id, "delete_list", f"Deleted list {target_list.name}")

    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
    finally:
        session.close()
