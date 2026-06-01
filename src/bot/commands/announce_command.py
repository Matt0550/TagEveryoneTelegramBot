from telegram import Update
from telegram.ext import ContextTypes
from decorators.cooldown import cooldown
from decorators.set_sentry_context import set_sentry_context
from decorators.is_owner import is_owner
from services.group_service import GroupService
from services.log_service import LogService
from utils.session_manager import Session
from utils.logger_base import logger

@set_sentry_context
@is_owner
@cooldown(15)
async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    try:
        message = update.message.text.replace("/announce ", "")
        if not message or message == "" or message == "/announce":
            await update.message.reply_text("You must specify a message")
            return

        groups = GroupService.get_all_groups(session)
        for group in groups:
            try:
                chat = await context.application.bot.get_chat(group.group_id)
                group_members = await chat.get_member_count()

                GroupService.update_group(
                    session,
                    group.group_id,
                    group_name=chat.title,
                    group_description=chat.description,
                    group_username=chat.username,
                    group_type=chat.type,
                    group_members=str(group_members),
                )

                await context.bot.send_message(group.group_id, message)
                logger.info(f"[MESSAGE] Message sent to group: {group.group_id}")
            except Exception as e:
                GroupService.delete_group(session, group.group_id)
                logger.error(f"[ERROR] {e}")
                continue

        await update.message.reply_text("Message sent to all groups")
        if update.message.chat:
            LogService.add_log(session, update.message.from_user.id, str(update.message.chat.id), "announce", "Message sent to all groups")

    finally:
        Session.remove()

@set_sentry_context
@is_owner
@cooldown(15)
async def checkGroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import asyncio
    session = Session()
    try:
        groups = GroupService.get_all_groups(session)
        working_groups = []
        failed_groups = []
        for group in groups:
            try:
                _chat = await context.bot.get_chat(group.group_id)
                working_groups.append(group.group_id)
            except Exception:
                failed_groups.append(group.group_id)
                GroupService.delete_group(session, group.group_id)
            await asyncio.sleep(0.1)

        await update.message.reply_text(f"Check completed.\nWorking groups: {len(working_groups)}\nFailed groups (removed): {len(failed_groups)}")
    finally:
        Session.remove()
