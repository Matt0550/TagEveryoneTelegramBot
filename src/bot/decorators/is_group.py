from telegram import Chat, Update
from telegram.ext import ContextTypes


def is_group(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Check if bot is in a group
        if update.effective_chat.type == Chat.GROUP or update.effective_chat.type == Chat.SUPERGROUP:
            # Check if bot is admin in the group
            member = await update.message.chat.get_member(context.application.bot.id)
            if member.status == "administrator":
                # Execute the function
                await func(update, context)
            else:
                await update.message.reply_text(
                    "The bot must be admin to use this command in a group")
        else:
            await update.message.reply_text(
                "❌ This command can only be used in a group.")
    return wrapper
