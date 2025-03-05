import logging
import os
import datetime
import traceback
from telegram import Update, Chat
from telegram.constants import ParseMode
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from db.databaseNew import Database
import dotenv

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()
OWNER_ID = os.getenv('owner_id')
TOKEN = os.getenv('token')

# Database instance
db = Database()

# Alternative @everyone commands
everyone_commands = ["@everyone", "@all", "/everyone", "/all"]

# Decorator to apply cooldown on commands
def cooldown(seconds):
    def decorator(func):
        last_time = {}

        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.message.from_user.id
            now = datetime.datetime.now()
            if user_id in last_time and now - last_time[user_id] < datetime.timedelta(seconds=seconds):
                await update.message.reply_text(f"You can use this command again in {seconds - (now - last_time[user_id]).seconds} seconds.")
                return
            last_time[user_id] = now
            await func(update, context)

        return wrapper
    return decorator

# Decorator to check if user is the bot owner
def is_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.message.from_user.id) == OWNER_ID:
            await func(update, context)
        else:
            await update.message.reply_text("You are not the bot owner.")
    return wrapper

# Global error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error while processing update: {context.error}")
    tb = traceback.format_exception(None, context.error, context.error.__traceback__)
    error_msg = f"Error:\n<pre>{''.join(tb)}</pre>"
    await context.bot.send_message(OWNER_ID, text=error_msg, parse_mode=ParseMode.HTML)

# Start command handler
@cooldown(15)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    db.create_user(user.id, user.first_name, user.last_name, user.username)
    if update.message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        await update.message.reply_text("Bot started in the group. Make sure it is an admin.")
    else:
        await update.message.reply_text("Welcome! Add the bot to a group to start using it.")

# Add user to list
@cooldown(15)
async def join_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    group = update.message.chat
    if user.username is None:
        await update.message.reply_text("You need to have a username to use this bot.")
        return

    db.add_member(group.id, group.title, user.id, user.username)
    await update.message.reply_text(f"You've been added to the list of group {group.title}.")

# Send message to all members in the list
@cooldown(15)
async def send_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.chat.id
    members = db.get_members(group_id)
    if members:
        for member in members:
            try:
                await update.message.chat.send_message(f"Message to everyone: {member}")
            except Exception as e:
                logger.error(f"Error sending message to {member}: {e}")
    else:
        await update.message.reply_text("No members in the list.")

# Help command handler
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
    Commands:
/in - Add yourself to the list
/out - Remove yourself from the list
/everyone - Send a message to all in the list
/list - Show the list of all members
/help - Show this help message
    """)

# Main function to start the bot
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join_list", join_list))
    application.add_handler(CommandHandler("send_to_all", send_to_all))
    application.add_handler(CommandHandler("help", help))
    application.add_error_handler(error_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
