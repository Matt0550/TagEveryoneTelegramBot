from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
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

        list_repo = ListRepository()
        user_list_repo = ListUserRepository()
        group_repo = GroupRepository()
        list_service = ListService(session, list_repo, user_list_repo, group_repo)

        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text("Group not registered.")
            return

        if not args:
            all_lists = list_service.get_active_lists(group.id)
            if not all_lists:
                await update.message.reply_text(
                    "There are no active lists in this group."
                )
                return

            text = "Available lists in this group:\n"
            for t_list in all_lists:
                text += f"- {t_list.name} (`/{t_list.trigger_name}`)\n"
            text += "\nTo see members of a list, type `/list <trigger_name>`"
            await update.message.reply_text(text, parse_mode="Markdown")
            return

        target_list_trigger = args[0].lower()
        if target_list_trigger.startswith("@"):
            target_list_trigger = target_list_trigger[1:]

        target_list = list_service.get_list_by_trigger_name(group.id, target_list_trigger)
        if not target_list:
            await update.message.reply_text(
                f"List <b>{target_list_trigger}</b> not found.", parse_mode="HTML"
            )
            return

        data = list_service.get_list_members(group.id, target_list.id)

        if not data:
            await update.message.reply_text(
                f"No one is in the <b>{target_list.name}</b> list", parse_mode="HTML"
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
                    f"Members of <b>{target_list.name}</b>:\n"
                    + "\n".join(members)
                    + "\n\nThanks for using this bot. Buy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot",
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )

            except Exception as e:
                logger.exception(f"[ERROR] list inner: {e}")
                await reply_generic_error(update)
    except Exception as e:
        logger.exception(f"[ERROR] list outer: {e}")
        await reply_generic_error(update)
    finally:
        session.close()
