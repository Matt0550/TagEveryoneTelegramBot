from functools import wraps

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes


def require_admin(func):
    """
    Decorator to check if the user executing the command is a group admin or creator.
    It must be used after @is_group if you also want to ensure it's a group,
    but this decorator itself also enforces the group check.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
            await update.message.reply_text("This command can only be used in a group.")
            return

        user_id = update.message.from_user.id

        try:
            member = await update.message.chat.get_member(user_id)
            if member.status not in ["administrator", "creator"]:
                await update.message.reply_text("You must be a group admin or owner to use this command.")
                return
        except TelegramError:
            await update.message.reply_text("Could not verify your admin status.")
            return

        return await func(update, context, *args, **kwargs)
    return wrapper
