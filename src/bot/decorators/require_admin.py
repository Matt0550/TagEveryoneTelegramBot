from functools import wraps

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from api.utils.telegram_utils import check_telegram_admin
from bot.i18n import get_locale, t


def require_admin(func):
    """
    Decorator to check if the user executing the command is a group admin or creator.
    It must be used after @is_group if you also want to ensure it's a group,
    but this decorator itself also enforces the group check.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
            if update.message:
                await update.message.reply_text(t("decorators.group_only", get_locale(update, context)))
            return

        user_id = update.effective_user.id if update.effective_user else None
        if not user_id:
            return

        try:
            is_admin = await check_telegram_admin(update.effective_chat.id, user_id, context.bot)
            if not is_admin:
                if update.message:
                    await update.message.reply_text(t("decorators.admin_only", get_locale(update, context)))
                return
        except TelegramError:
            if update.message:
                await update.message.reply_text(t("decorators.admin_check_failed", get_locale(update, context)))
            return

        return await func(update, context, *args, **kwargs)
    return wrapper
