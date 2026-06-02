from decorators.cooldown import cooldown
from decorators.is_group import is_group
from decorators.set_sentry_context import set_sentry_context
from telegram import MessageEntity, Update
from telegram.ext import ContextTypes

from models_all.group import GroupCreate
from models_all.list_user import ListUser
from models_all.user import UserCreate
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.group_service import GroupService
from services.log_service import LogService
from services.user_service import UserService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@set_sentry_context
@cooldown(15)
@is_group
async def join_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
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

        # Default to "everyone" list if no args provided or not mentioning user
        target_list_trigger = "everyone"
        mentioned_user = None

        if args:
            if args[0].startswith("@"):
                target_list_trigger = args[0][1:].lower()
            else:
                target_list_trigger = args[0].lower()

            # Check if an admin mentioned someone to add them
            entities = update.message.parse_entities(
                types=[MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
            )
            for entity, _value in entities.items():
                if entity.type == MessageEntity.TEXT_MENTION:
                    mentioned_user = entity.user
                elif entity.type == MessageEntity.MENTION:
                    pass  # We only support text mention right now, or we'd have to lookup by username

            if mentioned_user:
                # If they mentioned someone, default the list to everyone unless specified as second arg
                if len(args) > 1:
                    target_list_trigger = args[1].lower()
                else:
                    target_list_trigger = "everyone"

                admin_member = await update.message.chat.get_member(user_id)
                if admin_member.status not in [
                    admin_member.ADMINISTRATOR,
                    admin_member.OWNER,
                ]:
                    await update.message.reply_text(
                        "You must be a group admin or owner to add others."
                    )
                    return

        UserService.get_or_create_user(
            session,
            UserCreate(
                user_id=user_id,
                username=user_username,
                first_name=user_first_name,
                last_name=user_last_name,
            ),
        )
        group = GroupService.get_or_create_group(
            session,
            GroupCreate(
                telegram_id=group_id,
                group_name=group_name,
                group_description=group_description,
                group_username=group_username,
                group_type=group_type,
                group_members=group_members,
            ),
        )

        target_user_id = mentioned_user.id if mentioned_user else user_id
        if mentioned_user:
            UserService.get_or_create_user(
                session,
                UserCreate(
                    user_id=target_user_id,
                    username=mentioned_user.username,
                    first_name=mentioned_user.first_name,
                    last_name=mentioned_user.last_name,
                ),
            )

        list_repo = ListRepository()
        user_list_repo = ListUserRepository()

        target_list = list_repo.get_by_trigger_name(
            session, group.id, target_list_trigger
        )
        if not target_list:
            await update.message.reply_text(f"List '{target_list_trigger}' not found.")
            return

        existing = user_list_repo.get_subscription(
            session, target_list.id, target_user_id
        )
        if existing:
            await update.message.reply_text(
                f"User is already in the '{target_list.name}' list."
            )
            return

        user_list_repo.create(
            session, ListUser(list_id=target_list.id, user_id=target_user_id)
        )

        if mentioned_user:
            await update.message.reply_text(
                f"User manually added to '{target_list.name}'."
            )
        else:
            await update.message.reply_text(
                f"You have been added to '{target_list.name}'. To remove yourself type /out {target_list_trigger}"
            )

        LogService.add_log(
            session,
            user_id,
            group.id,
            "join_list",
            f"Added user {target_user_id} to list {target_list.name}",
        )
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        await update.message.reply_text(f"Error:\n`{e}`", parse_mode="Markdown")
    finally:
        session.close()
