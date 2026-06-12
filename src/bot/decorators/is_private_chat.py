from telegram import Chat, Update
from telegram.ext import ContextTypes

from bot.i18n import get_locale, t


def isPrivateChat(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Check if chat is private
        if update.effective_chat.type is Chat.PRIVATE:
            # Execute the function
            await func(update, context)
        else:
            await update.message.reply_text(
                t("decorators.private_only", get_locale(update, context)))
    return wrapper
