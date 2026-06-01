from telegram import Update, MessageEntity
from telegram.ext import ContextTypes
from utils.logger_base import logger
from decorators.cooldown import cooldown
from decorators.set_sentry_context import set_sentry_context
from decorators.is_group import is_group
from services.user_service import UserService
from services.group_service import GroupService
from services.log_service import LogService
from utils.session_manager import Session


@set_sentry_context
@cooldown(15)
@is_group
async def join_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    try:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        user_first_name = update.message.from_user.first_name
        user_last_name = update.message.from_user.last_name
        user_username = update.message.from_user.username
        group_name = update.message.chat.title
        chat = await context.application.bot.get_chat(group_id)
        group_description = chat.description
        group_username = update.message.chat.username
        group_type = update.message.chat.type
        group_members = await update.message.chat.get_member_count()
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

            if not mentioned_user:
                await update.message.reply_text(
                    "User not found. At the moment you can't add a user by username."
                )
                return

            UserService.get_or_create_user(
                session,
                mentioned_user.id,
                username=mentioned_user.username,
                first_name=mentioned_user.first_name,
                last_name=mentioned_user.last_name,
            )
            GroupService.get_or_create_group(
                session,
                str(group_id),
                group_name=group_name,
                group_description=group_description,
                group_username=group_username,
                group_type=group_type,
                group_members=str(group_members),
            )

            existing = GroupService.get_users_in_group(session, str(group_id))
            if any(u.user_id == mentioned_user.id for u in existing):
                await update.message.reply_text("User already in the list")
                return

            GroupService.add_user_to_group(session, str(group_id), mentioned_user.id)
            await update.message.reply_text("User manually added to the list")
            LogService.add_log(
                session,
                mentioned_user.id,
                str(group_id),
                "join_list",
                "User added to the list",
            )
            return

        UserService.get_or_create_user(
            session,
            user_id,
            username=user_username,
            first_name=user_first_name,
            last_name=user_last_name,
        )
        GroupService.get_or_create_group(
            session,
            str(group_id),
            group_name=group_name,
            group_description=group_description,
            group_username=group_username,
            group_type=group_type,
            group_members=str(group_members),
        )

        users_in_group = GroupService.get_users_in_group(session, str(group_id))
        if any(u.user_id == user_id for u in users_in_group):
            await update.message.reply_text("User already in the list")
            return

        GroupService.add_user_to_group(session, str(group_id), user_id)
        await update.message.reply_text(
            "You have been added to the list. To remove yourself from the list type /out\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot",
            disable_web_page_preview=True,
        )
        LogService.add_log(
            session, user_id, str(group_id), "join_list", "User added to the list"
        )
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
    finally:
        Session.remove()
