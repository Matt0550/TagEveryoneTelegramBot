import random

from decorators.cooldown import cooldown
from decorators.is_group import is_group
from decorators.set_sentry_context import set_sentry_context
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from models_all.user import UserCreate
from repositories.group_repository import GroupRepository
from repositories.list_repository import ListRepository
from repositories.list_user_repository import ListUserRepository
from services.group_service import GroupService
from services.log_service import LogService
from services.user_service import UserService
from utils.logger_base import logger
from utils.session_manager import Session, engine


async def triggerMessage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, matched_lists: list, group
):
    session = Session(engine)
    try:
        list_user_repo = ListUserRepository()

        # Collect unique user_ids from all matched lists
        user_ids = set()
        list_names = []
        for tag_list in matched_lists:
            list_names.append(tag_list.name)
            users = list_user_repo.get_users_in_list(session, tag_list.id)
            for u in users:
                user_ids.add(u.user_id)

        data = [
            {"user_id": uid} for uid in user_ids
        ]  # pseudo-user objects for compatibility

        random_number = random.randint(0, 5)
        donation_text = (
            "\n\nEnjoying this free bot? 🌟 Show your support by making a donation to help keep it running and improving! Every contribution matters. 🙏 Donate here: https://github.com/Matt0550/TagEveryoneTelegramBot#support-me"
            if random_number == 5
            else ""
        )

        if not data:
            await update.message.reply_text("No one is in the list")
        else:
            try:
                mentions = []
                for user in data:
                    try:
                        member = await update.message.chat.get_member(user["user_id"])
                        if member.user.username is not None:
                            UserService.get_or_create_user(
                                session,
                                UserCreate(
                                    user_id=user["user_id"],
                                    username=member.user.username,
                                ),
                            )
                        username = (
                            member.user.username
                            if member.user.username is not None
                            else user.get("username")
                        )
                    except Exception as e:
                        username = None
                        error_message_lower = str(e).lower()
                        if (
                            "member not found" in error_message_lower
                            or "participant_id_invalid" in error_message_lower
                        ):
                            GroupService().remove_user_from_group(
                                group.id, user["user_id"]
                            )
                            continue
                        continue

                    if user["user_id"] == update.effective_user.id:
                        mentions.append("You")
                    elif username is not None:
                        mentions.append(
                            f"<a href='tg://user?id={user['user_id']}'>@{username}</a>"
                        )
                    else:
                        mentions.append(
                            f"<a href='tg://user?id={user['user_id']}'>{user['user_id']}</a>"
                        )

                batch_size = 50
                for i in range(0, len(mentions), batch_size):
                    batch = mentions[i : i + batch_size]
                    user_mentions = "\n".join(batch)
                    if user_mentions:
                        await update.message.reply_text(
                            user_mentions + donation_text,
                            disable_web_page_preview=True,
                            parse_mode=ParseMode.HTML,
                        )

                LogService.add_log(
                    session,
                    update.message.from_user.id,
                    group.id,
                    "trigger_list",
                    f"Message sent to lists: {', '.join(list_names)}",
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


@set_sentry_context
@cooldown(15)
@is_group
async def everyone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.edited_message is not None or update.message is None:
            return
        if update.message.text is not None:
            text = update.message.text.lower()
            words = text.split()

            # Find all words that start with @ or /
            triggers = [w[1:] for w in words if w.startswith("@") or w.startswith("/")]
            if not triggers:
                return

            session = Session(engine)
            try:
                ListRepository()
                group_repo = GroupRepository()
                group = group_repo.get_by_telegram_id(session, update.message.chat.id)
                if not group:
                    return

                # Get all lists for this group
                from sqlmodel import select

                from models_all.tag_list import TagList

                statement = select(TagList).where(
                    TagList.group_id == group.id, TagList.active == True
                )
                all_lists = session.exec(statement).all()

                matched_lists = []
                for tag_list in all_lists:
                    # Check trigger name
                    if tag_list.trigger_name.lower() in triggers:
                        matched_lists.append(tag_list)
                    # Check aliases if implemented
                    elif tag_list.aliases:
                        try:
                            import json

                            aliases = json.loads(tag_list.aliases)
                            if any(a.lower() in triggers for a in aliases):
                                matched_lists.append(tag_list)
                        except:
                            pass

                if matched_lists:
                    await triggerMessage(update, context, matched_lists, group)
            finally:
                session.close()
    except Exception as e:
        logger.error(f"[ERROR] {e}")
