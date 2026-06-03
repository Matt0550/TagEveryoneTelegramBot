from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.decorators.require_admin import require_admin
from models_all.tag_list import TagList
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from services.log_service import LogService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@cooldown(5)
@is_group
@require_admin
async def createlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        args = context.args

        if not args or len(args) < 2:
            await update.message.reply_text(
                "Usage: /createlist <trigger_name> <List Name>\nExample: /createlist devs Developers List"
            )
            return

        trigger_name = args[0].lower()
        if trigger_name.startswith("@") or trigger_name.startswith("/"):
            trigger_name = trigger_name[1:]

        banned_words = [
            "start",
            "help",
            "admin",
            "settings",
            "lists",
            "in",
            "out",
            "createlist",
            "deletelist",
        ]
        if trigger_name in banned_words:
            await update.message.reply_text(
                "This trigger name is not allowed as it conflicts with bot commands."
            )
            return

        name = " ".join(args[1:])

        list_repo = ListRepository()
        group_repo = GroupRepository()
        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text(
                "Group not registered. Type /in everyone to initialize it first."
            )
            return

        existing = list_repo.get_by_trigger_name(session, group.id, trigger_name)
        if existing:
            await update.message.reply_text(
                f"A list with the trigger '{trigger_name}' already exists."
            )
            return

        new_list = TagList(group_id=group.id, name=name, trigger_name=trigger_name)
        list_repo.create(session, new_list)

        await update.message.reply_text(
            f"List '{name}' created successfully! Users can now type `/in {trigger_name}` to join.",
            parse_mode="Markdown",
        )
        LogService.add_log(
            session, user_id, group.id, "create_list", f"Created list {name}"
        )

    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
    finally:
        session.close()
