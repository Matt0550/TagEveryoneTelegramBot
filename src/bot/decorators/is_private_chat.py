from telegram import Chat, Update
from telegram.ext import ContextTypes


def isPrivateChat(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Check if chat is private
        if update.effective_chat.type is Chat.PRIVATE:
            # Execute the function
            await func(update, context)
        else:
            await update.message.reply_text(
                "This command can only be used in a private chat")
    return wrapper
