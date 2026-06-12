from telegram import Update
from telegram.ext import ContextTypes

from api.utils.telegram_utils import check_telegram_admin
from bot.decorators.cooldown import cooldown
from bot.i18n import get_locale, t
from models_all.user import UserCreate
from services.log_service import LogService
from services.user_service import UserService
from utils.logger_base import logger
from utils.session_manager import Session, engine


@cooldown(15)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        user_id = update.message.from_user.id
        first_name = update.message.from_user.first_name
        last_name = update.message.from_user.last_name
        username = update.message.from_user.username
        chat_id = update.message.chat.id

        UserService.get_or_create_user(
            session,
            UserCreate(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
            ),
        )

        locale = get_locale(update, context)

        if update.message.chat.type not in ["group", "supergroup"]:
            await update.message.reply_text(
                t("start.welcome_private", locale)
            )
        else:
            is_bot_admin = await check_telegram_admin(chat_id, context.application.bot.id, context.application.bot)
            if is_bot_admin:
                await update.message.reply_text(
                    t("start.ready", locale)
                )
            else:
                try:
                    await update.message.reply_text(
                        t("errors.bot_must_be_admin", locale)
                    )
                except Exception:
                    try:
                        await context.application.bot.send_message(
                            chat_id=user_id,
                            text=t("start.must_be_admin_dm", locale),
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
