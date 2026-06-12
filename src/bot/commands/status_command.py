import datetime

from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.i18n import get_locale, t
from services.log_service import LogService
from utils.session_manager import Session, engine

start_time = datetime.datetime.now()


@cooldown(15)
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        uptime = datetime.datetime.now() - start_time
        uptime = str(uptime).split(".")[0]

        await update.message.reply_text(
            t("status.text", get_locale(update, context), uptime=uptime),
            disable_web_page_preview=True,
        )

        LogService.add_log(
            session,
            update.message.from_user.id,
            str(update.message.chat.id),
            "status",
            "Status sent",
        )
    finally:
        session.close()
