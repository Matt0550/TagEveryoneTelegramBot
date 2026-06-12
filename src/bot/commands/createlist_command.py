from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.decorators.require_admin import require_admin
from bot.i18n import get_locale, t
from bot.utils.args import parse_trigger_name
from bot.utils.errors import reply_generic_error
from models_all.tag_list import TagListCreate
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.list_service import ListService
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
        locale = get_locale(update, context)

        if not args or len(args) < 2:
            await update.message.reply_text(
                t("createlist.usage", locale)
            )
            return

        trigger_name = parse_trigger_name(args)

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
                t("createlist.banned_word", locale)
            )
            return

        name = " ".join(args[1:])

        list_repo = ListRepository()
        group_repo = GroupRepository()
        user_list_repo = ListUserRepository()
        list_service = ListService(session, list_repo, user_list_repo, group_repo)

        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text(
                t("groups.not_registered_init", locale)
            )
            return

        existing = list_repo.get_by_trigger_name(session, group.id, trigger_name)
        if existing:
            await update.message.reply_text(
                t("createlist.already_exists", locale, trigger=trigger_name)
            )
            return

        tag_list_create = TagListCreate(group_id=group.id, name=name, trigger_name=trigger_name)
        list_service.create_list(user_id=user_id, obj_in=tag_list_create)

        await update.message.reply_text(
            t("createlist.created", locale, name=name, trigger=trigger_name),
            parse_mode="Markdown",
        )

    except Exception as e:
        logger.exception(f"[ERROR] createlist: {e}")
        await reply_generic_error(update, context)
    finally:
        session.close()
