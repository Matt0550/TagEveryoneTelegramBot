from telegram import MessageEntity, Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.log_service import LogService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@cooldown(15)
@is_group
async def leave_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        user_id = update.message.from_user.id
        group_id = update.message.chat.id
        args = context.args

        # Default to "everyone" list if no args provided or not mentioning user
        target_list_trigger = "everyone"
        mentioned_user = None

        if args:
            if args[0].startswith("@"):
                target_list_trigger = args[0][1:].lower()
            else:
                target_list_trigger = args[0].lower()

            entities = update.message.parse_entities(
                types=[MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
            )
            for entity, _value in entities.items():
                if entity.type == MessageEntity.TEXT_MENTION:
                    mentioned_user = entity.user

            if mentioned_user:
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
                        "You must be a group admin or owner to remove others."
                    )
                    return

        target_user_id = mentioned_user.id if mentioned_user else user_id

        list_repo = ListRepository()
        user_list_repo = ListUserRepository()
        group_repo = GroupRepository()

        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text("Group not registered.")
            return

        target_list = list_repo.get_by_trigger_name(
            session, group.id, target_list_trigger
        )
        if not target_list:
            await update.message.reply_text(f"List '{target_list_trigger}' not found.")
            return

        existing = user_list_repo.get_subscription(
            session, target_list.id, target_user_id
        )
        if not existing:
            await update.message.reply_text(
                f"User is not in the '{target_list.name}' list."
            )
            return

        user_list_repo.delete(session, existing.id)

        if mentioned_user:
            await update.message.reply_text(
                f"User manually removed from '{target_list.name}'."
            )
        else:
            await update.message.reply_text(
                f"You have been removed from '{target_list.name}'. To add yourself type /in {target_list_trigger}"
            )

        LogService.add_log(
            session,
            user_id,
            group.id,
            "leave_list",
            f"Removed user {target_user_id} from list {target_list.name}",
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
        session.close()
