from decorators.cooldown import cooldown
from decorators.set_sentry_context import set_sentry_context
from telegram import Update
from telegram.ext import ContextTypes

from services.log_service import LogService
from services.user_service import UserService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@set_sentry_context
@cooldown(15)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        user_id = update.message.from_user.id
        first_name = update.message.from_user.first_name
        last_name = update.message.from_user.last_name
        username = update.message.from_user.username
        chat_id = update.message.chat.id

        from models_all.user import UserCreate
        UserService.get_or_create_user(
            session,
            UserCreate(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )
        )

        if update.message.chat.type not in ["group", "supergroup"]:
            await update.message.reply_text(
                "Welcome to Tag Everyone Bot\n\nFor more information type /help\n\nTo get started add this bot as ADMIN to a group and type /in to get started."
            )
        else:
            member_status = await update.message.chat.get_member(
                context.application.bot.id
            )
            if member_status.status == "administrator":
                await update.message.reply_text(
                    "Bot is now ready to use.\nFor more information type /help"
                )
            else:
                try:
                    await update.message.reply_text(
                        "The bot must be admin to use this command in a group"
                    )
                except Exception:
                    try:
                        await context.application.bot.send_message(
                            chat_id=user_id,
                            text="The bot must be admin to use this command in a group. Please add the bot as admin and try again.",
                        )
                    except Exception as e:
                        logger.error(f"[ERROR] {e}")
                        return

        LogService.add_log(
            session, user_id, str(chat_id), "start", "User started the bot"
        )
    except Exception as e:
        logger.error(f"[ERROR] {e}")
    finally:
        session.close()
