from telegram import Update, MessageEntity
from telegram.ext import ContextTypes
from utils.logger_base import logger
from decorators.cooldown import cooldown
from decorators.set_sentry_context import set_sentry_context
from decorators.is_group import is_group
from services.group_service import GroupService
from services.log_service import LogService
from utils.session_manager import Session


@set_sentry_context
@cooldown(15)
@is_group
async def leave_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    try:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        args = context.args

        if args:
            admin_member = await update.message.chat.get_member(user_id)
            if admin_member.status not in [
                admin_member.ADMINISTRATOR,
                admin_member.OWNER,
            ]:
                await update.message.reply_text(
                    "You must be a group admin or owner to use this command"
                )
                return

            entities = update.message.parse_entities(
                types=[MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
            )
            mentioned_user = None

            for entity, value in entities.items():
                if entity.type == MessageEntity.TEXT_MENTION:
                    mentioned_user = entity.user
                elif entity.type == MessageEntity.MENTION:
                    # Non-trivial to resolve username to ID without DB search
                    pass

            if not mentioned_user:
                await update.message.reply_text(
                    "You need to mention a user! (Note: @username tagging may not find the user, try replying or using their name)"
                )
                return

            existing = GroupService.get_users_in_group(session, str(group_id))
            if not any(u.user_id == mentioned_user.id for u in existing):
                await update.message.reply_text("User not found in the list")
                return

            GroupService.remove_user_from_group(
                session, str(group_id), mentioned_user.id
            )
            await update.message.reply_text("User manually removed from the list")
            LogService.add_log(
                session,
                mentioned_user.id,
                str(group_id),
                "leave_list",
                "User removed from the list",
            )
        else:
            existing = GroupService.get_users_in_group(session, str(group_id))
            if not any(u.user_id == user_id for u in existing):
                await update.message.reply_text("You are not in the list")
                return

            GroupService.remove_user_from_group(session, str(group_id), user_id)
            await update.message.reply_text(
                "You have been removed from the list. To add yourself to the list type /in\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot",
                disable_web_page_preview=True,
            )
            LogService.add_log(
                session,
                user_id,
                str(group_id),
                "leave_list",
                "User removed from the list",
            )

    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
        try:
            LogService.add_log(
                session,
                update.message.from_user.id,
                str(update.message.chat.id),
                "error",
                str(e),
            )
        except Exception:
            pass
    finally:
        Session.remove()
