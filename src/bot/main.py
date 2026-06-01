import sentry_sdk
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,
)
import traceback
import html
import json
import os
import sys

# Add the src directory to the sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_base import logger


from utils.config import settings

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        send_default_pii=True,
    )
    logger.info("Sentry initialized")

from commands.start_command import start
from commands.help_command import help as help_cmd
from commands.status_command import status
from commands.stats_command import stats
from commands.in_command import join_list
from commands.out_command import leave_list
from commands.everyone_command import everyone, everyoneMessage
from commands.list_command import getList
from commands.announce_command import announce, checkGroups


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    if not settings.REPORT_ERRORS_OWNER or not settings.OWNER_ID:
        return

    try:
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        tb_string = "".join(tb_list)
        update_str = update.to_dict() if isinstance(update, Update) else str(update)

        max_update_str_length = 1000
        max_tb_length = 2000

        if (
            len(json.dumps(update_str, indent=2, ensure_ascii=False))
            > max_update_str_length
        ):
            update_str = {"truncated": "Update object too large to display"}

        if len(tb_string) > max_tb_length:
            tb_string = tb_string[:max_tb_length] + "\n... [TRUNCATED]"

        message = (
            "An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data)[:500])}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data)[:500])}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        if len(message) > 4000:
            message = (
                f"🚨 Bot Error Occurred\n\n"
                f"<b>Error Type:</b> {type(context.error).__name__}\n"
                f"<b>Error Message:</b> {html.escape(str(context.error)[:500])}\n\n"
                f"<b>Traceback (shortened):</b>\n"
                f"<pre>{html.escape(tb_string[:1500])}</pre>"
            )

        await context.bot.send_message(
            chat_id=settings.OWNER_ID, text=message, parse_mode="HTML"
        )

    except Exception as error_in_handler:
        logger.error(f"Error in error_handler: {error_in_handler}")


def main():
    logger.info("Starting bot...")
    application = Application.builder().token(settings.BOT_TOKEN).build()

    application.add_error_handler(error_handler)

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("in", join_list))
    application.add_handler(CommandHandler("out", leave_list))
    application.add_handler(CommandHandler("everyone", everyoneMessage))
    application.add_handler(CommandHandler("all", everyoneMessage))
    application.add_handler(CommandHandler("list", getList))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("announce", announce))
    application.add_handler(CommandHandler("checkGroups", checkGroups))

    # Message handlers for triggers (like @everyone)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, everyone))

    if settings.ENABLE_WEBAPP_SERVER:
        # Run the webapp in a separate thread
        from threading import Thread
        import gui

        webapp_thread = Thread(target=gui.mainGUI)
        webapp_thread.daemon = True
        webapp_thread.start()
        logger.info("Webapp thread started")

    logger.info("Bot started successfully!")
    application.run_polling()


if __name__ == "__main__":
    logger.info("Tag Everyone Telegram Bot")
    logger.info("Developed by @Non_Sono_Matteo")
    logger.info("https://matt05.it")
    main()
