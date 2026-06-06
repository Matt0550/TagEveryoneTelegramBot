from telegram import MessageEntity, Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from repositories.user_repository import UserRepository
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

        target_list_trigger = "everyone"

        target_user_id = user_id
        is_manual_modify = False

        if args:
            entities = update.message.parse_entities(
                types=[MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
            )
            mentioned_user_obj = None
            mentioned_username = None

            for entity, value in entities.items():
                if entity.type == MessageEntity.TEXT_MENTION:
                    mentioned_user_obj = entity.user
                elif entity.type == MessageEntity.MENTION:
                    mentioned_username = value[1:]

            if mentioned_user_obj:
                target_user_id = mentioned_user_obj.id
                is_manual_modify = True
            elif mentioned_username:
                user_repo = UserRepository()
                db_user = user_repo.get_by_username(session, mentioned_username)
                if db_user:
                    target_user_id = db_user.user_id
                    is_manual_modify = True
                else:
                    await update.message.reply_text(
                        f"User @{mentioned_username} not found in bot database."
                    )
                    return
            elif args[0].isdigit():
                target_user_id = int(args[0])
                is_manual_modify = True

            if is_manual_modify:
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
            else:
                if args[0].startswith("@"):
                    target_list_trigger = args[0][1:].lower()
                else:
                    target_list_trigger = args[0].lower()

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

        if is_manual_modify:
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
