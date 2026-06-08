from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.decorators.require_admin import require_admin
from bot.utils.args import parse_trigger_name
from bot.utils.errors import reply_generic_error
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.list_service import ListService
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

        trigger_name = parse_trigger_name(args)

        list_repo = ListRepository()
        user_list_repo = ListUserRepository()
        group_repo = GroupRepository()
        list_service = ListService(session, list_repo, user_list_repo, group_repo)

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

        cleared_count = list_service.clear_list(user_id=user_id, group_id=group.id, list_id=existing.id)

        if cleared_count != -1:
            await update.message.reply_text(
                f"List <b>{existing.name}</b> cleared successfully. Removed {cleared_count} users.",
                parse_mode="HTML",
            )
        else:
            await update.message.reply_text(
                f"Could not clear list <b>{existing.name}</b>.",
                parse_mode="HTML",
            )

    except Exception as e:
        logger.exception(f"[ERROR] clearlist: {e}")
        await reply_generic_error(update)
    finally:
        session.close()
