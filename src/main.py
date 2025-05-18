#################################
#   Tag Everyone Telegram Bot   #
# Developed by @Non_Sono_Matteo #
#   https://matteosillitti.it   #
#       Github: @Matt0550       #
#################################

from telegram import Update, Chat, MessageEntity
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler, ChatMemberHandler
from db.databaseNew import Database
import json
import datetime
import dotenv
import logging
import os
import traceback
import html
import random


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d - %(funcName)s)",
    level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Load .env file
dotenv.load_dotenv()
# set your owner_id and token to docker-compose.yml and start it
OWNER_ID = os.environ['owner_id']  # or insert owner id to OWNER_ID
TOKEN = os.environ['token']        # and insert token to TOKEN
# and just run main.py

# set WEB_SERVER_REPLIT to 1 if you want to host the bot on replit
ENABLE_WEBAPP_SERVER = os.environ['enable_webapp_server']
REPORT_ERRORS_OWNER = os.environ['report_errors_owner']


# Create an istance of database
db = Database()

global everyoneCommands

# everyoneCommands = ["@everyone", "@all", "/everyone", "/all", "/everyone@"+application.bot.username, "/all@" +
#                 application.bot.username, "@"+application.bot.username]  # You can add more aliases for the command /everyone

# You can add more aliases for the command /everyone
everyoneCommands = ["@everyone", "@all", "/everyone", "/all"]

start_time = datetime.datetime.now()  # For the uptime command

# Create a decorator to apply cooldown to a function (in seconds) for user who used the command


def cooldown(seconds):
    def decorator(func):
        # Create a dictionary to store the last time the user used the command
        last_time = {}

        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.edited_message != None or update.message == None:
                # If the message is edited, return
                return
            
            if any(comm in update.message.text.lower() for comm in everyoneCommands) or update.message.text.startswith("/"):
                # Get the user id
                user_id = update.message.from_user.id
                if user_id == OWNER_ID:
                    # If the user is the owner, execute the function
                    await func(update, context)
                    return
                # Get the current time
                now = datetime.datetime.now()
                # Check if the user has used the command before
                if user_id in last_time:
                    # Check if the user has used the command in the last seconds
                    if now - last_time[user_id] < datetime.timedelta(seconds=seconds):
                        # If the user has used the command in the last seconds, send a message to the user
                        await update.message.reply_text("You can use this command again in %s seconds" % str(
                            seconds - (now - last_time[user_id]).seconds))
                        # Return to avoid the function to be executed
                        return
                # Update the last time the user used the command
                last_time[user_id] = now
                # Execute the function
                await func(update, context)
        return wrapper
    return decorator

# Create a decorator to check if the bot is admin and if the bot is in a group


def group(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Check if bot is in a group
        if update.effective_chat.type == Chat.GROUP or update.effective_chat.type == Chat.SUPERGROUP:
            # Check if bot is admin in the group
            member = await update.message.chat.get_member(context.application.bot.id)
            if member.status == "administrator":
                # Execute the function
                await func(update, context)
            else:
                await update.message.reply_text(
                    "The bot must be admin to use this command in a group")
        else:
            await update.message.reply_text(
                "This command can only be used in a group")
    return wrapper

# Create a decorator to check if the user is owner and is private chat


def isOwner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Check if user is owner
        if str(update.message.from_user.id) == str(OWNER_ID):
            # Check if chat is private
            if update.effective_chat.type is Chat.PRIVATE:
                # Execute the function
                await func(update, context)
            else:
                await update.message.reply_text(
                    "This command can only be used in a private chat")
        else:
            await update.message.reply_text("You are not the owner of the bot")
    return wrapper


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML
    )


@cooldown(15)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log user
    db.createUser(update.message.from_user.id, update.message.from_user.first_name,
                  update.message.from_user.last_name, update.message.from_user.username)

    # Check if bot is in a group
    if not update.message.chat.type == "group" or not update.message.chat.type == "supergroup":
        await update.message.reply_text(
            "Welcome to Tag Everyone Bot\n\nFor more information type /help\n\nTo get started add this bot to a group and type /start in the group")
    else:
        # Check if bot is admin in the group
        if update.message.chat.get_member(context.application.bot.id).status == "administrator":
            await update.message.reply_text(
                "Bot is now ready to use.\nFor more information type /help")
        else:
            await update.message.reply_text(
                "The bot must be admin to use this command in a group")

    db.logEvent(update.message.from_user.id, update.message.chat.id,
                "start", "User started the bot")

    
@cooldown(15)
@group
# Function to add a member to the list
async def join_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get the user id and group id from the message
        user_id = update.message.from_user.id
        group_id = update.message.chat.id

        user_first_name = update.message.from_user.first_name
        user_last_name = update.message.from_user.last_name
        user_username = update.message.from_user.username

        group_name = update.message.chat.title
        chat = await context.application.bot.get_chat(group_id)
        group_description = chat.description
        group_username = update.message.chat.username
        group_type = update.message.chat.type
        group_members = await update.message.chat.get_member_count()

        # Optional command args if user has tagged a username
        args = context.args

        if args:
            # Check if the user who sent the command is an admin inside the group
            admin_member = await update.message.chat.get_member(user_id)

            if admin_member.status != admin_member.ADMINISTRATOR and admin_member.status != admin_member.OWNER:
                await update.message.reply_text(
                    "You must be a group admin or owner to use this command")
                return
            
            entities = update.message.parse_entities(types=[MessageEntity.TEXT_MENTION, MessageEntity.MENTION])

            mentioned_user = None

            for entity, value in entities.items():
                if entity.type == MessageEntity.TEXT_MENTION:
                    mentioned_user = entity.user
                
            if not mentioned_user:
                await update.message.reply_text("User not found. At the moment you can't add a user by username.")
                return
            
            # Check if the user is already in the list
            data = db.getUser(mentioned_user.id)
            if data:
                await update.message.reply_text("User already in the list")
                return
            # Insert data into database
            db.insertData(group_id, group_name, group_description, group_username, group_type,
                        group_members, mentioned_user.id, mentioned_user.first_name, mentioned_user.last_name, mentioned_user.username)
            logger.info("[DATABAE] Inserted data into database: %s, %s" %
                        (group_id, mentioned_user.id))
            await update.message.reply_text(
                "User manually added to the list")
            db.logEvent(mentioned_user.id, group_id, "join_list",
                        "User added to the list")
            return
        
        # Check if the user is already in the list
        data = db.getUser(user_id)
        if data:
            await update.message.reply_text("You are already in the list")
            return

        #if user_username == None:
        #    await update.message.reply_text("You must have an username to use this bot. Please set an username in your Telegram settings")
        #    return

        # Remove from group id "-" and convert to int
        
        # Insert data into database
        db.insertData(group_id, group_name, group_description, group_username, group_type,
                      group_members, user_id, user_first_name, user_last_name, user_username)

        logger.info("[DATABAE] Inserted data into database: %s, %s" %
                    (group_id, user_id))

        await update.message.reply_text(
            "You have been added to the list. To remove yourself from the list type /out\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot", disable_web_page_preview=True)

        db.logEvent(user_id, group_id, "join_list", "User added to the list")
    except Exception as e:
        logger.error("[ERROR] " + str(e))

        await update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")


@cooldown(15)
@group
# Function to remove a member from the list
async def leave_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get the user id and group id from the message
        user_id = update.message.from_user.id
        group_id = update.message.chat.id

        # Optional command args if user has tagged a username
        args = context.args

        if args:
            # Check if the user who sent the command is an admin inside the group
            admin_member = await update.message.chat.get_member(user_id)

            if admin_member.status != admin_member.ADMINISTRATOR and admin_member.status != admin_member.OWNER:
                await update.message.reply_text(
                    "You must be a group admin or owner to use this command")
                return
            
            entities = update.message.parse_entities(types=[MessageEntity.TEXT_MENTION, MessageEntity.MENTION])

            mentioned_user = None

            for entity, value in entities.items():

                if entity.type == MessageEntity.TEXT_MENTION:
                    mentioned_user = entity.user
                elif entity.type == MessageEntity.MENTION:
                    username = value.lstrip("@")
                    try:
                        user_db = db.getUserByUsername(username)

                        if user_db:
                            mentioned_user = await update.message.chat.get_member(int(user_db[0][1]))
                            mentioned_user = mentioned_user.user
                        else:
                            await update.message.reply_text("User not found in the list")
                            return
                    except Exception as e:
                        logger.error("[ERROR] " + str(e))
                        await update.message.reply_text("Failed to find username by @username.")
                        return

            if not mentioned_user:
                await update.message.reply_text("You need to mention a user!")
                return
            
            # Check if the user is in the list
            data = db.getUser(mentioned_user.id)
            if not data:
                await update.message.reply_text("User not found in the list")
                return
            # Remove from the list
            db.deleteData(group_id, mentioned_user.id)
            logger.info("[DATABAE] Deleted data from database: %s, %s" %
                        (group_id, user_id))
            
            await update.message.reply_text(
                "User manually removed from the list")
            
            db.logEvent(mentioned_user.id, group_id, "leave_list",
                        "User removed from the list")
            
        else:
            # Delete data from database
            db.deleteData(group_id, user_id)

            logger.info("[DATABAE] Deleted data from database: %s, %s" %
                        (group_id, user_id))

            await update.message.reply_text(
                "You have been removed from the list. To add yourself to the list type /in\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot", disable_web_page_preview=True)

            db.logEvent(user_id, group_id, "leave_list",
                        "User removed from the list")
        
    except Exception as e:
        logger.error("[ERROR] " + str(e))
        # Print error with code markup
        await update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

        db.logEvent(user_id, group_id, "error", str(e))


@cooldown(15)
@group
async def everyoneMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get the group id from the message
        group_id = update.message.chat.id
        # Get data from database
        data = db.getMembers(group_id)

        logger.info("[DATABASE] Got data from database: %s" % group_id)

        # Get a random number from 0 to 5
        random_number = random.randint(0, 5)
        donation_text = (
            "\n\nEnjoying this free bot? 🌟 Show your support by making a donation to help keep it running and improving! Every contribution matters. 🙏 Donate here: https://github.com/Matt0550/TagEveryoneTelegramBot#support-me"
            if random_number == 5
            else ""
        )

        if not data:
            await update.message.reply_text("No one is in the list")
        else:
            try:
                mentions = []
                for user in data:
                    try:
                        logger.info("[USER] Looking for user: %s" % user[0])
                        member = await update.message.chat.get_member(int(user[0]))
                        # update with recent username
                        if member.user.username != None:
                            db.updateUserUsername(user[0], member.user.username)
                        
                        username = member.user.username if member.user.username != None else user[1]
                    except Exception as e:
                        logger.info("[USER] " + str(e) + " - below user")
                        logger.info(user)
                        username = None

                        # If member not found, delete from database
                        error_message_lower = str(e).lower()

                        if "member not found" in error_message_lower or "participant_id_invalid" in error_message_lower:
                            db.deleteData(group_id, user[0])
                            logger.info("[DATABASE] Deleted user %s from database for group %s due to: %s" % (user[0], group_id, e))
                            continue
                        continue

                    # do not tag the user who sent the command
                    if int(user[0]) == update.effective_user.id:
                        mentions.append("You")
                    elif username != None:
                        # If user has username, use it
                        mentions.append(f"<a href='tg://user?id={user[0]}'>@{username}</a>")
                    elif user[2] != None:
                        # Else, use first name, last name or ID. in each case use markdown to tag with id
                        text = f"{user[2]}"
                        if user[3] != None:
                            text += f" {user[3]}"
                        mentions.append(f"<a href='tg://user?id={user[0]}'>{text}</a>")
                    else:
                        # If user has no username or name, use their ID
                        mentions.append(f"<a href='tg://user?id={user[0]}'>{user[0]}</a>")

                # Send mentions in batches of 50
                batch_size = 50
                for i in range(0, len(mentions), batch_size):
                    batch = mentions[i:i + batch_size]
                    user_mentions = "\n".join(batch)
                    
                    # Check if message is not empty and send it
                    if user_mentions:
                        await update.message.reply_text(
                            user_mentions + donation_text,
                            disable_web_page_preview=True,
                            parse_mode=ParseMode.HTML,
                        )

                # members = []
                # # Iterate tuple
                # for i in data:
                #     print(i)
                #     # Append to members list the username of the member
                #     try:
                #         member = await update.message.chat.get_member(int(i[0]))
                #         if member.user.username != None:
                #             members.append(
                #                 "@" + member.user.username)
 
                #     except Exception as e:
                #         logger.info("[USER] " + str(e) + " - " + str(i))
                #         continue

                # # If the members are more than 50 send the message in multiple messages
                # if len(members) > 50:
                #     # Create a list of lists with 50 members each
                #     members = [members[i:i + 50]
                #                for i in range(0, len(members), 50)]
                #     # Iterate the list of lists
                #     for i in members:
                #         # Send message with list of members
                #         await update.message.reply_text("\n".join(
                #             i) + donation_text, disable_web_page_preview=True)
                # else:
                #     # Send message with list of members
                #     await update.message.reply_text("\n".join(
                #         members) + donation_text, disable_web_page_preview=True)

                db.logEvent(update.message.from_user.id, group_id,
                            "everyone", "Message sent to all in the list")

            except Exception as e:
                logger.error("[ERROR] " + str(e))

                await update.message.reply_text(
                    "Error:\n`%s`" % e, parse_mode="Markdown")

                db.logEvent(update.message.from_user.id,
                            group_id, "error", str(e))
    except Exception as e:
        logger.error("[ERROR] " + str(e))
        # Print error with code markup
        await update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

        db.logEvent(update.message.from_user.id, group_id, "error", str(e))


async def everyone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if is edited message
        if update.edited_message != None or update.message == None:
            return
        
        if update.message.text != None:
            # Check if message contains any of the commands in the list (case insensitive)
            if any(comm.lower() in update.message.text.lower() for comm in everyoneCommands) or any(comm in update.message.text for comm in everyoneCommands):
                # Apply cooldown only if the message is in the list (command)
                await everyoneMessage(update, context)
            else:
                return
        else:
            return
    except Exception as e:
        logger.error("[ERROR] " + str(e))


@cooldown(15)
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


@cooldown(15)
async def getList(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get the group id from the message
        group_id = update.message.chat.id
        # Get data from database
        data = db.getMembers(group_id)

        logger.info("[DATABASE] Got data from database: %s" % group_id)

        if not data:
            await update.message.reply_text("No one is in the list")
        else:
            try:
                members = []
                # Iterate tuple
                for i in data:
                    # Append to members list the username of the member
                    try:
                        member = await update.message.chat.get_member(int(i[0]))

                        username = member.user.username if member.user.username != None else member.user.full_name
                        members.append(username)
                    
                    except Exception as e:
                        logger.warning("[USER] " + str(e) + " - " + str(i))

                        # If member not found, delete from database
                        if "Member not found".lower() in str(e).lower():
                            db.deleteData(group_id, i[0])
                            logger.info("[DATABASE] Deleted user from database: %s" % i[0])
                            continue

                        continue
                # Send message with list of members
                await update.message.reply_text("\n".join(
                    members) + "\n\nThanks for using this bot. Buy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot", disable_web_page_preview=True)

                db.logEvent(update.message.from_user.id,
                            group_id, "list", "List sent")
            except Exception as e:
                logger.error("[ERROR] " + str(e))
                await update.message.reply_text(
                    "Error:\n`%s`" % e, parse_mode="Markdown")

                db.logEvent(update.message.from_user.id,
                            group_id, "error", str(e))

    except Exception as e:
        logger.error("[ERROR] " + str(e))
        # Print error with code markup
        await update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")


@cooldown(15)
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the bot uptime widout microseconds
    uptime = datetime.datetime.now() - start_time
    uptime = str(uptime).split(".")[0]

    await update.message.reply_text("✅ If you see this message, the bot is working\n⏰ Uptime: %s" % str(
        uptime) + "\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot", disable_web_page_preview=True)

    db.logEvent(update.message.from_user.id,
                update.message.chat.id, "status", "Status sent")


@cooldown(60)
@isOwner
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_groups = db.getTotalGroups()
    total_members = db.getTotalUsers()

    await update.message.reply_text("Total active groups: %s\nTotal active members: %s" % (total_groups, total_members) +
                                    "\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550\nSource code: https://github.com/Matt0550/TagEveryoneTelegramBot", disable_web_page_preview=True)

    db.logEvent(update.message.from_user.id,
                update.message.chat.id, "stats", "Stats sent")


@isOwner
@cooldown(15)
async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the message
    message = update.message.text.replace("/announce ", "")
    if not message or message == "" or message == "/announce":
        await update.message.reply_text("You must specify a message")
        return
    # Get all groups from database
    groups = db.getAllGroups()
    # Iterate all groups
    for group in groups:
        try:
            # Update group info in db
            # Send message to group id
            group_id = update.message.chat.id
            group_name = update.message.chat.title
            chat = await context.application.bot.get_chat(group_id)
            group_description = chat.description
            group_username = update.message.chat.username
            group_type = update.message.chat.type
            group_members = await update.message.chat.get_member_count()

            db.updateGroupInfo(group_id, group_name, group_description,
                               group_username, group_type, group_members)
            await context.bot.send_message(group[1], message)
            logger.info("[MESSAGE] Message sent to group: %s" % group[1])
        except Exception as e:
            db.deleteGroup(group[1])
            logger.error("[ERROR] " + str(e))
            continue
    await update.message.reply_text("Message sent to all groups")

    db.logEvent(update.message.from_user.id, update.message.chat.id,
                "announce", "Message sent to all groups")


@isOwner
@cooldown(15)
async def checkGroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get all groups from database
    groups = db.getAllGroups()
    working_groups = []
    args = context.args
    # Iterate all groups
    for group in groups:
        try:
            chat = await context.bot.get_chat(group[1])

            group_id = chat.id
            group_name = chat.title
            group_description = chat.description
            group_username = chat.username
            group_type = chat.type
            group_members = await chat.get_member_count()

            db.updateGroupInfo(group_id, group_name, group_description,
                               group_username, group_type, group_members)
            working_groups.append(group[1])
            logger.info("[MESSAGE] Checked group: %s" % group[1])

        except Exception as e:
            # If args true delete group from database
            if args and args[0] == "delete":
                # Delete group from database
                db.deleteGroup(group[1])
                logger.info("[DATABASE] Deleted group from database: %s" % group[1])
            
            logger.error("[ERROR] " + str(e))
            continue

    await update.message.reply_text("Working groups: %s\n\nNot working groups: %s" % (len(working_groups), len(groups) - len(working_groups)))

    db.logEvent(update.message.from_user.id, update.message.chat.id,
                "checkGroups", "Checked all groups")

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_change = update.chat_member
    old_status = status_change.old_chat_member.status
    new_status = status_change.new_chat_member.status
    user = status_change.new_chat_member.user

    logger.info("[CHAT_MEMBER] User %s changed status from %s to %s" %
                (user.id, old_status, new_status))
    
    if old_status == ChatMemberStatus.LEFT and new_status == ChatMemberStatus.MEMBER:
        # Check if user is in the list
        data = db.getUser(user.id)
        if not data:
            chat = await context.application.bot.get_chat(update.chat_member.chat.id)

            # Insert data into database
            db.insertData(update.chat_member.chat.id, chat.title, chat.description, chat.username, chat.type,
                        await chat.get_member_count(), user.id, user.first_name, user.last_name, user.username)
            logger.info("[DATABAE] Inserted data into database: %s, %s" %
                        (update.chat_member.chat.id, user.id))
                  
            await context.bot.send_message(chat_id=update.chat_member.chat.id, text=f"{user.full_name} was added to the list.")

    elif new_status == ChatMemberStatus.LEFT or new_status == ChatMemberStatus.BANNED:
        # Check if user is in the list
        data = db.getUser(user.id)
        if data:
            # Delete data from database
            db.deleteData(update.chat_member.chat.id, user.id)
            logger.info("[DATABAE] Deleted data from database: %s, %s" %
                        (update.chat_member.chat.id, user.id))
            
            await context.bot.send_message(chat_id=update.chat_member.chat.id, text=f"{user.full_name} has been removed from the list.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('everyone', everyone))
    application.add_handler(CommandHandler('all', everyone))
    application.add_handler(CommandHandler('in', join_list))
    application.add_handler(CommandHandler('out', leave_list))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('stats', stats))
    application.add_handler(CommandHandler('list', getList))
    application.add_handler(CommandHandler('announce', announce))
    application.add_handler(CommandHandler('checkGroups', checkGroups))

    application.add_handler(MessageHandler(filters.TEXT, everyone))
    
    application.add_handler(ChatMemberHandler(chat_member_update, ChatMemberHandler.CHAT_MEMBER))

    if REPORT_ERRORS_OWNER == True or REPORT_ERRORS_OWNER == "1" or REPORT_ERRORS_OWNER.lower() == "true":
        application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    print("Tag Everyone Telegram Bot")
    print("Developed by @Non_Sono_Matteo")
    print("https://matteosillitti.it")
    if ENABLE_WEBAPP_SERVER == True or ENABLE_WEBAPP_SERVER == "1" or ENABLE_WEBAPP_SERVER.lower() == "true":
        from gui import mainGUI
        from threading import Thread
        t = Thread(target=mainGUI)
        t.start()
    # Start bot
    main()
