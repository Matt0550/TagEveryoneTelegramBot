from telegram import MessageEntity, Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.i18n import get_locale, t
from bot.utils.errors import reply_generic_error
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from repositories.user_repository import UserRepository
from services.list_service import ListService
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
        locale = get_locale(update, context)

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
                        t("users.not_found", locale, username=mentioned_username)
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
                        t("out.must_be_admin_modify", locale)
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
        list_service = ListService(session, list_repo, user_list_repo, group_repo)

        group = group_repo.get_by_telegram_id(session, group_id)
        if not group:
            await update.message.reply_text(t("groups.not_registered", locale))
            return

        target_list = list_service.get_list_by_trigger_name(group.id, target_list_trigger)
        if not target_list:
            await update.message.reply_text(t("lists.not_found", locale, trigger=target_list_trigger))
            return

        success = list_service.unsubscribe(
            user_id=target_user_id, group_id=group.id, list_id=target_list.id
        )

        if not success:
            await update.message.reply_text(
                t("out.not_in_list", locale, list=target_list.name)
            )
            return

        if is_manual_modify:
            await update.message.reply_text(
                t("out.manual_removed", locale, list=target_list.name)
            )
        else:
            await update.message.reply_text(
                t("out.removed_self", locale, list=target_list.name, trigger=target_list_trigger)
            )

    except Exception as e:
        logger.exception(f"[ERROR] leave_list: {e}")
        await reply_generic_error(update, context)
    finally:
        session.close()
