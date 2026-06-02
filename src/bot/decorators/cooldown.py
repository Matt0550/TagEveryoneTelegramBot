from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from utils.config import settings


def cooldown(seconds):
    def decorator(func):
        if settings.ENVIRONMENT == "local":
            return func
        # Create a dictionary to store the last time the user used the command
        last_time = {}

        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.edited_message is not None or update.message is None:
                return

            if update.message.text is None:
                return

            # Check if the message contains specific commands or starts with "/"
            should_apply_cooldown = False
            if settings.EVERYONE_COMMANDS_TEXTS:
                if any(comm in update.message.text.lower() for comm in settings.EVERYONE_COMMANDS_TEXTS) or update.message.text.startswith("/"):
                    should_apply_cooldown = True
            else:
                # If no commands specified, apply to all messages
                should_apply_cooldown = True

            if should_apply_cooldown:
                # Get the user id
                tg_user_id = update.message.from_user.id
                if settings.OWNER_ID and tg_user_id == settings.OWNER_ID:
                    # If the user is the owner, execute the function without cooldown
                    await func(update, context)
                    return
                # Get the current time
                now = datetime.now()
                # Check if the user has used the command before
                if tg_user_id in last_time:
                    # Check if the user has used the command in the last seconds
                    if now - last_time[tg_user_id] < timedelta(seconds=seconds):
                        # If the user has used the command in the last seconds, send a message to the user
                        await update.message.reply_text("You can use this command again in {} seconds".format(str(
                            seconds - (now - last_time[tg_user_id]).seconds)))
                        # Return to avoid the function to be executed
                        return
                # Update the last time the user used the command
                last_time[tg_user_id] = now
            # Execute the function
            await func(update, context)
        return wrapper
    return decorator
