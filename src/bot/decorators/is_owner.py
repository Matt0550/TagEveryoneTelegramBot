from telegram import Update
from telegram.ext import ContextTypes
from telegram import Chat
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
                    "This command can only be used in a private chat")
        else:
            await update.message.reply_text("❌ You are not authorized to use this command.")
    return wrapper