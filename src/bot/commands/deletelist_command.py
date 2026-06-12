from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.decorators.require_admin import require_admin
from bot.i18n import get_locale, t
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
async def deletelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        args = context.args
        locale = get_locale(update, context)

        if not args:
            await update.message.reply_text(t("deletelist.usage", locale))
            return

        trigger_name = args[0].lower()
        if trigger_name.startswith("@") or trigger_name.startswith("/"):
            trigger_name = trigger_name[1:]

        group_repo = GroupRepository()
        list_repo = ListRepository()
        user_list_repo = ListUserRepository()
        list_service = ListService(session, list_repo, user_list_repo, group_repo)

        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text(t("groups.not_registered", locale))
            return

        target_list = list_repo.get_by_trigger_name(session, group.id, trigger_name)

        if not target_list:
            await update.message.reply_text(t("lists.not_found", locale, trigger=trigger_name))
            return

        try:
            success = list_service.delete_list(user_id=user_id, group_id=group.id, list_id=target_list.id)
            if success:
                await update.message.reply_text(
                    t("deletelist.deleted", locale, list=target_list.name)
                )
            else:
                await update.message.reply_text(
                    t("deletelist.delete_failed", locale, list=target_list.name)
                )
        except ValueError as e:
            # The only expected ValueError is the system-list guard; localize it
            # but fall back to the raw message for anything unforeseen.
            if "system list" in str(e).lower():
                await update.message.reply_text(t("lists.cannot_delete_system", locale))
            else:
                await update.message.reply_text(str(e))

    except Exception as e:
        logger.exception(f"[ERROR] deletelist: {e}")
        await reply_generic_error(update, context)
    finally:
        session.close()
