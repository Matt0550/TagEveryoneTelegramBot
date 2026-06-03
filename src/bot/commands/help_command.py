from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown


@cooldown(15)
async def help(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
    Tag Everyone Telegram Bot\n
Commands:
/in - Add yourself to the Everyone's list
/out - Remove yourself from the Everyone's list\n
/everyone - Send a message to all in the list
/all - Send a message to all in the list
/list - Show the list of everyone's list (without metion)\n
/help - Show this message
/status - Show the status of the bot
/stats - Show the stats of the bot\n
Triggers:
@everyone - Send a message to all in the list
@all - Send a message to all in the list\n
This project is open source and free to use.
Follow updates on News channel: @tageveryone_news\n
Developed by @Non_Sono_Matteo
https://matteosillitti.it

Source code: https://github.com/Matt0550/TagEveryoneTelegramBot
Buy me a coffee: https://buymeacoffee.com/Matt0550
""")
