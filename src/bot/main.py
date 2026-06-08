import os
import sys

# Add the src directory to the sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sentry_sdk
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    TypeHandler,
    filters,
)

from bot.instance import build_application
from bot.middlewares.activity_middleware import activity_middleware
from bot.middlewares.sentry_middleware import sentry_middleware
from bot.utils.errors import notify_owner_of_error, reply_generic_error
from utils.config import settings
from utils.logger_base import logger

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        send_default_pii=True,
    )
    logger.info("Sentry initialized")

from telegram.ext import ChatMemberHandler

from bot.commands.announce_command import announce, announce_status, checkGroups
from bot.commands.clearlist_command import clearlist
from bot.commands.createlist_command import createlist
from bot.commands.deletelist_command import deletelist
from bot.commands.everyone_command import everyone
from bot.commands.help_command import help as help_cmd
from bot.commands.in_command import join_list
from bot.commands.list_command import getList
from bot.commands.out_command import leave_list
from bot.commands.settings_command import settings_command
from bot.commands.start_command import start
from bot.commands.stats_command import stats
from bot.commands.status_command import status
from bot.handlers.chat_member_handler import chat_member_handler, my_chat_member_handler


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Central error handler.

    Logs the full traceback server-side, replies to the user with a generic
    message (never the raw exception), and optionally forwards a detailed
    report to the bot owner DM when configured.

    :param update: the originating ``Update`` object (or ``None``).
    :param context: telegram-ext context carrying the exception.
    """
    logger.error("Exception while handling an update:", exc_info=context.error)
    tg_update = update if isinstance(update, Update) else None
    await reply_generic_error(tg_update)
    if context.error is not None:
        await notify_owner_of_error(
            bot=context.bot,
            exc=context.error,
            update=tg_update,
            context_data={
                "chat_data": str(context.chat_data)[:300] if context.chat_data else None,
                "user_data": str(context.user_data)[:300] if context.user_data else None,
            },
        )


def main():
    logger.info("Starting bot...")
    application = build_application()

    application.add_error_handler(error_handler)

    # Global middlewares
    application.add_handler(TypeHandler(Update, sentry_middleware), group=-1)
    application.add_handler(TypeHandler(Update, activity_middleware), group=-2)

    # Chat member handlers
    application.add_handler(ChatMemberHandler(my_chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(ChatMemberHandler(chat_member_handler, ChatMemberHandler.CHAT_MEMBER))

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("in", join_list))
    application.add_handler(CommandHandler("out", leave_list))
    application.add_handler(CommandHandler("list", getList))
    application.add_handler(CommandHandler("lists", getList))
    application.add_handler(CommandHandler("createlist", createlist))
    application.add_handler(CommandHandler("deletelist", deletelist))
    application.add_handler(CommandHandler("clearlist", clearlist))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("announce", announce))
    application.add_handler(CommandHandler("announce_status", announce_status))
    application.add_handler(CommandHandler("checkGroups", checkGroups))
    application.add_handler(CommandHandler("settings", settings_command))

    # Message handlers for triggers (like @everyone or /everyone)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, everyone))
    # Note: we also want to catch dynamic /commands that are not registered.
    # To do this, we can add a MessageHandler for filters.COMMAND that isn't caught by others.
    application.add_handler(MessageHandler(filters.COMMAND, everyone))

    logger.info("Bot started successfully!")
    application.run_polling(
        allowed_updates=[
            Update.MESSAGE,
            Update.CALLBACK_QUERY,
            Update.MY_CHAT_MEMBER,
            Update.CHAT_MEMBER,
        ]
    )


if __name__ == "__main__":
    logger.info("Tag Everyone Telegram Bot")
    logger.info("Developed by @Non_Sono_Matteo")
    logger.info("https://matt05.it")
    main()
