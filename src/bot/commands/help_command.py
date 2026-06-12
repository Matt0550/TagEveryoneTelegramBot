from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.i18n import get_locale, t


@cooldown(15)
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(t("help.text", get_locale(update, context)))
