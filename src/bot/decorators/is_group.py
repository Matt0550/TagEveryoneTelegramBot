from telegram import Chat, Update
from telegram.ext import ContextTypes

from api.utils.telegram_utils import check_telegram_admin


def is_group(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Check if bot is in a group
        if not update.effective_chat or update.effective_chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
            if update.message:
                await update.message.reply_text("❌ This command can only be used in a group.")
            return

        # Check if bot is admin in the group
        is_bot_admin = await check_telegram_admin(update.effective_chat.id, context.application.bot.id, context.application.bot)
        if is_bot_admin:
            # Execute the function
            await func(update, context)
        else:
            if update.message:
                await update.message.reply_text("The bot must be admin to use this command in a group")
    return wrapper
