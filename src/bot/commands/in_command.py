from telegram import MessageEntity, Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.i18n import get_locale, t
from bot.utils.errors import reply_generic_error
from models_all.group import GroupCreate
from models_all.user import UserCreate
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from repositories.user_repository import UserRepository
from services.group_service import GroupService
from services.list_service import ListService
from services.user_service import UserService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@cooldown(15)
@is_group
async def join_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.from_user is None:
        return
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
        locale = get_locale(update, context)

        target_list_trigger = "everyone"

        target_user_id = user_id
        target_username = user_username
        target_first_name = user_first_name
        target_last_name = user_last_name
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
                target_username = mentioned_user_obj.username
                target_first_name = mentioned_user_obj.first_name
                target_last_name = mentioned_user_obj.last_name
                is_manual_modify = True
            elif mentioned_username:
                user_repo = UserRepository()
                db_user = user_repo.get_by_username(session, mentioned_username)
                if db_user:
                    target_user_id = db_user.user_id
                    target_username = db_user.username
                    target_first_name = db_user.first_name
                    target_last_name = db_user.last_name
                    is_manual_modify = True
                else:
                    await update.message.reply_text(
                        t("users.not_found", locale, username=mentioned_username)
                    )
                    return
            elif args[0].isdigit():
                target_user_id = int(args[0])
                is_manual_modify = True
                user_repo = UserRepository()
                db_user = user_repo.get_by_user_id(session, target_user_id)
                if db_user:
                    target_username = db_user.username
                    target_first_name = db_user.first_name
                    target_last_name = db_user.last_name

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
                        t("in.must_be_admin_modify", locale)
                    )
                    return
            else:
                if args[0].startswith("@"):
                    target_list_trigger = args[0][1:].lower()
                else:
                    target_list_trigger = args[0].lower()

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

        if is_manual_modify:
            UserService.get_or_create_user(
                session,
                UserCreate(
                    user_id=target_user_id,
                    username=target_username,
                    first_name=target_first_name,
                    last_name=target_last_name,
                ),
            )

        list_repo = ListRepository()
        user_list_repo = ListUserRepository()
        group_repo = GroupRepository()
        list_service = ListService(session, list_repo, user_list_repo, group_repo)

        target_list = list_service.get_list_by_trigger_name(group.id, target_list_trigger)
        if not target_list:
            await update.message.reply_text(t("lists.not_found", locale, trigger=target_list_trigger))
            return

        success = list_service.subscribe(
            user_id=target_user_id, group_id=group.id, list_id=target_list.id
        )

        if not success:
            await update.message.reply_text(
                t("in.already_in_list", locale, list=target_list.name)
            )
            return

        if is_manual_modify:
            await update.message.reply_text(
                t("in.manual_added", locale, list=target_list.name)
            )
        else:
            await update.message.reply_text(
                t("in.added_self", locale, list=target_list.name, trigger=target_list_trigger)
            )

    except Exception as e:
        logger.exception(f"[ERROR] join_list: {e}")
        await reply_generic_error(update, context)
    finally:
        session.close()
