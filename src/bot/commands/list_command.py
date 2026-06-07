from sqlmodel import select
from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from models_all.tag_list import TagList
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.log_service import LogService
from services.mention_service import MentionService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@cooldown(15)
async def getList(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        group_id = update.message.chat.id
        args = context.args
        list_repo = ListRepository()

        group_repo = GroupRepository()
        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text("Group not registered.")
            return

        if not args:
            statement = select(TagList).where(
                TagList.group_id == group.id, TagList.active == True
            )
            all_lists = session.exec(statement).all()
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

        target_list = list_repo.get_by_trigger_name(
            session, group.id, target_list_trigger
        )
        if not target_list:
            await update.message.reply_text(
                f"List <b>{target_list_trigger}</b> not found.", parse_mode="HTML"
            )
            return

        user_list_repo = ListUserRepository()
        data = user_list_repo.get_users_in_list(session, target_list.id)

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

                LogService.add_log(
                    session,
                    update.message.from_user.id,
                    group.id,
                    "list",
                    f"List {target_list.name} members sent",
                )
            except Exception as e:
                logger.error(f"[ERROR] {e}")
                await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
                LogService.add_log(
                    session, update.message.from_user.id, group.id, "error", str(e)
                )
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
    finally:
        session.close()
