from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.decorators.require_admin import require_admin
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.log_service import LogService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@cooldown(5)
@is_group
@require_admin
async def clearlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        args = context.args

        if not args:
            await update.message.reply_text(
                "Usage: /clearlist <trigger_name>\nExample: /clearlist devs"
            )
            return

        trigger_name = args[0].lower()
        if trigger_name.startswith("@") or trigger_name.startswith("/"):
            trigger_name = trigger_name[1:]

        list_repo = ListRepository()
        user_list_repo = ListUserRepository()
        group_repo = GroupRepository()

        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text(
                "Group not registered. Type /in everyone to initialize it first."
            )
            return

        existing = list_repo.get_by_trigger_name(session, group.id, trigger_name)
        if not existing:
            await update.message.reply_text(
                f"List '{trigger_name}' not found."
            )
            return

        cleared_count = user_list_repo.clear_list_subscriptions(session, existing.id)
        session.commit()

        await update.message.reply_text(
            f"List <b>{existing.name}</b> cleared successfully. Removed {cleared_count} users.",
            parse_mode="HTML",
        )
        LogService.add_log(
            session, user_id, group.id, "clear_list", f"Cleared {cleared_count} users from list {existing.name}"
        )

    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
    finally:
        session.close()
