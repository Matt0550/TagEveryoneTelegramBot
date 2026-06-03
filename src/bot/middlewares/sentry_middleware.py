import sentry_sdk
from telegram import Update
from telegram.ext import ContextTypes

from utils.config import settings


async def sentry_middleware(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Middleware to set Sentry user context for every incoming update."""
    if settings.SENTRY_DSN:
        user_info = None
        chat_info = None

        if update.effective_user:
            user_info = {
                "id": update.effective_user.id,
                "username": update.effective_user.username,
                "full_name": update.effective_user.full_name,
            }

        if update.effective_chat:
            chat_info = {
                "id": update.effective_chat.id,
                "title": update.effective_chat.title,
                "type": update.effective_chat.type,
            }

        sentry_sdk.set_user(user_info)
        sentry_sdk.set_context("chat", chat_info)
