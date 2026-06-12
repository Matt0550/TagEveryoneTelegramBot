from telegram import Chat, Update
from telegram.ext import ContextTypes

from bot.i18n import get_locale, t
from utils.config import settings


def is_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Check if user is owner
        if str(update.message.from_user.id) == str(settings.OWNER_ID):
            # Check if chat is private
            if update.effective_chat.type is Chat.PRIVATE:
                # Execute the function
                await func(update, context)
            else:
                await update.message.reply_text(
                    t("decorators.private_only", get_locale(update, context)))
        else:
            await update.message.reply_text(t("decorators.not_authorized", get_locale(update, context)))
    return wrapper
