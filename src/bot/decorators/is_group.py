from telegram import Chat, Update
from telegram.ext import ContextTypes

from api.utils.telegram_utils import check_telegram_admin
from bot.i18n import get_locale, t


def is_group(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Check if bot is in a group
        if not update.effective_chat or update.effective_chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
            if update.message:
                await update.message.reply_text(t("decorators.group_only", get_locale(update, context)))
            return

        # Check if bot is admin in the group
        is_bot_admin = await check_telegram_admin(update.effective_chat.id, context.application.bot.id, context.application.bot)
        if is_bot_admin:
            # Execute the function
            await func(update, context)
        else:
            if update.message:
                await update.message.reply_text(t("errors.bot_must_be_admin", get_locale(update, context)))
    return wrapper
