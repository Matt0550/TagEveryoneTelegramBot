from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.i18n import get_locale, t
from bot.utils.errors import reply_generic_error
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.list_service import ListService
from services.mention_service import MentionService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@cooldown(15)
@is_group
async def getList(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        group_id = update.message.chat.id
        args = context.args
        locale = get_locale(update, context)

        list_repo = ListRepository()
        user_list_repo = ListUserRepository()
        group_repo = GroupRepository()
        list_service = ListService(session, list_repo, user_list_repo, group_repo)

        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text(t("groups.not_registered", locale))
            return

        if not args:
            all_lists = list_service.get_active_lists(group.id)
            if not all_lists:
                await update.message.reply_text(
                    t("list.no_active_lists", locale)
                )
                return

            text = t("list.available_header", locale)
            for t_list in all_lists:
                text += f"- {t_list.name} (`/{t_list.trigger_name}`)\n"
            text += t("list.footer_hint", locale)
            await update.message.reply_text(text, parse_mode="Markdown")
            return

        target_list_trigger = args[0].lower()
        if target_list_trigger.startswith("@"):
            target_list_trigger = target_list_trigger[1:]

        target_list = list_service.get_list_by_trigger_name(group.id, target_list_trigger)
        if not target_list:
            await update.message.reply_text(
                t("list.list_not_found", locale, trigger=target_list_trigger), parse_mode="HTML"
            )
            return

        data = list_service.get_list_members(group.id, target_list.id)

        if not data:
            await update.message.reply_text(
                t("list.empty_list", locale, list=target_list.name), parse_mode="HTML"
            )
        else:
            try:
                user_ids = {u.user_id for u in data}
                members = await MentionService.build_mentions(
                    session=session,
                    group_id=group.id,
                    group_telegram_id=group.telegram_id,
                    user_ids=user_ids,
                    update=update,
                    plain_text=True,
                )

                await update.message.reply_text(
                    t("list.members_header", locale, list=target_list.name)
                    + "\n"
                    + "\n".join(members)
                    + t("common.thanks_footer", locale),
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )

            except Exception as e:
                logger.exception(f"[ERROR] list inner: {e}")
                await reply_generic_error(update, context)
    except Exception as e:
        logger.exception(f"[ERROR] list outer: {e}")
        await reply_generic_error(update, context)
    finally:
        session.close()
