from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from api.utils.telegram_utils import check_telegram_admin
from bot.decorators.cooldown import cooldown
from bot.decorators.is_group import is_group
from bot.i18n import get_locale, t
from repositories.group_repository import GroupRepository
from utils.config import settings
from utils.logger_base import logger
from utils.session_manager import Session, engine


@cooldown(15)
@is_group
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    locale = get_locale(update, context)

    try:
        # Check if user is admin.
        is_admin = await check_telegram_admin(chat_id, user_id, context.bot)
        if not is_admin:
            return

        session = Session(engine)
        try:
            group_repo = GroupRepository()
            group = group_repo.get_by_telegram_id(session, chat_id)
            if not group:
                return

            bot_username = context.bot.username
            # Using the webapp shortname configured in config (and .env)
            deeplink = f"https://t.me/{bot_username}/{settings.WEBAPP_SHORTNAME}?startapp={group.id}"

            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(t("settings.button", locale), url=deeplink)]]
            )
            text = t("settings.manage", locale, group=update.message.chat.title)

            sent_in_private = False
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )
                sent_in_private = True
            except Exception as e:
                logger.info(f"Could not send private message to user {user_id}: {e}")

            if sent_in_private:
                try:
                    await update.message.delete()
                except Exception as e:
                    logger.warning(f"Could not delete message in group {chat_id}: {e}")
            else:
                await update.message.reply_text(
                    text=t("settings.cant_dm", locale),
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

        finally:
            session.close()

    except Exception as e:
        logger.error(f"[ERROR] in settings command: {e}")
