#################################
#   Tag Everyone Telegram Bot   #
# Developed by @Non_Sono_Matteo #
#       https://matt05.it       #
#       Github: @Matt0550       #
#################################

from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from databaseNew import Database
import json
import datetime
import dotenv
import os

# Load .env file
dotenv.load_dotenv()
# set your owner_id and token to docker-compose.yml and start it
OWNER_ID = os.environ['owner_id']  # or insert owner id to OWNER_ID
TOKEN = os.environ['token']        # and insert token to TOKEN
# and just run main.py

# set WEB_SERVER_REPLIT to 1 if you want to host the bot on replit
WEB_SERVER_REPLIT = os.environ['web_server_replit']
# set SEND_MESSAGE_OWNER to 1 if you want to send a message to the owner when the bot starts
SEND_MESSAGE_OWNER = os.environ['send_message_owner']

if WEB_SERVER_REPLIT == True or WEB_SERVER_REPLIT == "true":
    from keep_alive import keep_alive  # Replit hosting

# Create an istance of database
db = Database()

updater = Updater(TOKEN, use_context=True)

everyoneCommands = ["@everyone", "@all", "/everyone", "/all", "/everyone@"+updater.bot.username, "/all@" +
                    updater.bot.username, "@"+updater.bot.username]  # You can add more aliases for the command /everyone

start_time = datetime.datetime.now()  # For the uptime command

# Create a decorator to apply cooldown to a function (in seconds) for user who used the command
def cooldown(seconds):
    def decorator(func):
        # Create a dictionary to store the last time the user used the command
        last_time = {}

        def wrapper(update: Update, context: CallbackContext):
            if any(comm in update.message.text.lower() for comm in everyoneCommands) or update.message.text.startswith("/"):
                # Get the user id
                user_id = update.message.from_user.id
                # Get the current time
                now = datetime.datetime.now()
                # Check if the user has used the command before
                if user_id in last_time:
                    # Check if the user has used the command in the last seconds
                    if now - last_time[user_id] < datetime.timedelta(seconds=seconds):
                        # If the user has used the command in the last seconds, send a message to the user
                        update.message.reply_text("You can use this command again in %s seconds" % str(
                            seconds - (now - last_time[user_id]).seconds))
                        # Return to avoid the function to be executed
                        return
                # Update the last time the user used the command
                last_time[user_id] = now
                # Execute the function
                func(update, context)
        return wrapper
    return decorator

# Create a decorator to check if the bot is admin and if the bot is in a group


def group(func):
    def wrapper(update: Update, context: CallbackContext):
        # Check if bot is in a group
        if update.message.chat.type == "group" or update.message.chat.type == "supergroup":
            # Check if bot is admin in the group
            if update.message.chat.get_member(updater.bot.id).status == "administrator":
                # Execute the function
                func(update, context)
            else:
                update.message.reply_text(
                    "The bot must be admin to use this command in a group")
        else:
            update.message.reply_text(
                "This command is can only be used in a group")
    return wrapper

# Create a decorator to check if the user is owner and is private chat


def isOwner(func):
    def wrapper(update: Update, context: CallbackContext):
        # Check if user is owner
        if str(update.message.from_user.id) == str(OWNER_ID):
            # Check if chat is private
            if update.message.chat.type == "private":
                # Execute the function
                func(update, context)
            else:
                update.message.reply_text(
                    "This command can only be used in a private chat")
        else:
            update.message.reply_text("You are not the owner of the bot")
    return wrapper


@cooldown(15)
def start(update: Update, context: CallbackContext):
    # Log user
    db.createUser(update.message.from_user.id, update.message.from_user.first_name,
                  update.message.from_user.last_name, update.message.from_user.username)
    # Check if bot is in a group
    if not update.message.chat.type == "group" or not update.message.chat.type == "supergroup":
        update.message.reply_text(
            "Please add me to a group with admin permissions")
    else:
        # Check if bot is admin in the group
        if update.message.chat.get_member(updater.bot.id).status == "administrator":
            update.message.reply_text(
                "Bot is now ready to use.\nFor more information type /help")
        else:
            update.message.reply_text(
                "The bot must be admin to use this command in a group")

    db.logEvent(update.message.from_user.id, update.message.chat.id,
                "start", "User started the bot")


@cooldown(15)
@group
# Function to add a member to the list
def join_list(update: Update, context: CallbackContext):
    try:
        # Get the user id and group id from the message
        user_id = update.message.from_user.id
        user_first_name = update.message.from_user.first_name
        user_last_name = update.message.from_user.last_name
        user_username = update.message.from_user.username

        # Remove from group id "-" and convert to int
        group_id = update.message.chat.id
        group_name = update.message.chat.title
        group_description = update.message.chat.description
        group_username = update.message.chat.username
        group_type = update.message.chat.type
        group_members = update.message.chat.get_members_count()

        # Insert data into database
        db.insertData(group_id, group_name, group_description, group_username, group_type,
                      group_members, user_id, user_first_name, user_last_name, user_username)
        print("[DATABASE] Inserted data into database: %s, %s" %
              (group_id, user_id))
        update.message.reply_text(
            "You have been added to the list. To remove yourself from the list type /out\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550", disable_web_page_preview=True)

        db.logEvent(user_id, group_id, "join_list", "User added to the list")
    except Exception as e:
        print("[ERROR] " + str(e))
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

        db.logEvent(user_id, group_id, "error", str(e))


@cooldown(15)
@group
# Function to remove a member from the list
def leave_list(update: Update, context: CallbackContext):
    try:
        # Get the user id and group id from the message
        user_id = update.message.from_user.id

        # Remove from group id "-" and convert to int
        group_id = update.message.chat.id
        # Delete data from database
        db.deleteData(group_id, user_id)
        print("[DATABAE] Deleted data from database: %s, %s" %
              (group_id, user_id))
        update.message.reply_text(
            "You have been removed from the list. To add yourself to the list type /in\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550", disable_web_page_preview=True)

        db.logEvent(user_id, group_id, "leave_list",
                    "User removed from the list")
    except Exception as e:
        print("[ERROR] " + str(e))
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

        db.logEvent(user_id, group_id, "error", str(e))


@cooldown(15)
@group
def everyoneMessage(update: Update, context: CallbackContext):
    try:
        # Get the group id from the message
        group_id = update.message.chat.id
        # Get data from database
        data = db.getMembers(group_id)
        print("[DATABASE] Got data from database: %s" % group_id)

        if not data:
            update.message.reply_text("No one is in the list")
        else:
            try:
                members = []
                # Iterate tuple
                for i in data:
                    # Append to members list the username of the member
                    try:
                        members.append(
                            "@" + update.message.chat.get_member(int(i[0])).user.username)
                    except Exception as e:
                        print("[USER] " + str(e) + " - " + str(i))
                        continue

                # If the members are more than 50 send the message in multiple messages
                if len(members) > 50:
                    # Create a list of lists with 50 members each
                    members = [members[i:i + 50]
                               for i in range(0, len(members), 50)]
                    # Iterate the list of lists
                    for i in members:
                        # Send message with list of members
                        update.message.reply_text("\n".join(
                            i) + "\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550", disable_web_page_preview=True)
                else:
                    # Send message with list of members
                    update.message.reply_text("\n".join(
                        members) + "\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550", disable_web_page_preview=True)

                db.logEvent(update.message.from_user.id, group_id,
                            "everyone", "Message sent to all in the list")

            except Exception as e:
                print("[ERROR] " + str(e))
                update.message.reply_text(
                    "Error:\n`%s`" % e, parse_mode="Markdown")

                db.logEvent(update.message.from_user.id,
                            group_id, "error", str(e))

    except Exception as e:
        print("[ERROR] " + str(e))
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

        db.logEvent(update.message.from_user.id, group_id, "error", str(e))


def everyone(update: Update, context: CallbackContext):
    if update.message.text != None:
        # Check if message contains any of the commands in the list (case insensitive)
        if any(comm.lower() in update.message.text.lower() for comm in everyoneCommands) or any(comm in update.message.text for comm in everyoneCommands):
            # Apply cooldown only if the message is in the list (command)
            everyoneMessage(update, context)
        else:
            return
    else:
        return


@cooldown(15)
def help(update: Update, context: CallbackContext):
    update.message.reply_text("""
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
Developed by @Non_Sono_Matteo
https://matt05.it
Github: @Matt0550
Buy me a coffee: https://buymeacoffee.com/Matt0550
""")

    db.logEvent(update.message.from_user.id,
                update.message.chat.id, "help", "Help sent")

@cooldown(15)
def getList(update: Update, context: CallbackContext):
    try:
        # Get the group id from the message
        group_id = update.message.chat.id
        # Get data from database
        data = db.getMembers(group_id)
        print("[DATABASE] Got data from database: %s" % group_id)

        if not data:
            update.message.reply_text("No one is in the list")
        else:
            try:
                members = []
                # Iterate tuple
                for i in data:
                    # Append to members list the username of the member
                    try:
                        members.append(update.message.chat.get_member(
                            int(i[0])).user.username)
                    except Exception as e:
                        print("[USER] " + str(e) + " - " + str(i))
                        continue
                # Send message with list of members
                update.message.reply_text("\n".join(
                    members) + "\n\nThanks for using this bot. Buy me a coffee: https://buymeacoffee.com/Matt0550", disable_web_page_preview=True)

                db.logEvent(update.message.from_user.id,
                            group_id, "list", "List sent")
            except Exception as e:
                print("[ERROR] " + str(e))
                update.message.reply_text(
                    "Error:\n`%s`" % e, parse_mode="Markdown")

                db.logEvent(update.message.from_user.id,
                            group_id, "error", str(e))

    except Exception as e:
        print("[ERROR] " + str(e))
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

@cooldown(15)
def status(update: Update, context: CallbackContext):
    # Get the bot uptime widout microseconds
    uptime = datetime.datetime.now() - start_time
    uptime = str(uptime).split(".")[0]

    update.message.reply_text("✅ If you see this message, the bot is working\n⏰ Uptime: %s" % str(
        uptime) + "\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550", disable_web_page_preview=True)

    db.logEvent(update.message.from_user.id,
                update.message.chat.id, "status", "Status sent")

@cooldown(60)
def stats(update: Update, context: CallbackContext):
    total_groups = db.getTotalGroups()
    total_members = db.getTotalUsers()

    update.message.reply_text("Total active groups: %s\nTotal active members: %s" % (total_groups, total_members) +
                              "\n\nThanks for using this bot.\nBuy me a coffee: https://buymeacoffee.com/Matt0550", disable_web_page_preview=True)

    db.logEvent(update.message.from_user.id,
                update.message.chat.id, "stats", "Stats sent")

@isOwner
@cooldown(1)
def announce(update: Update, context: CallbackContext):
    # Get the message
    message = update.message.text.replace("/announce ", "")
    if not message or message == "" or message == "/announce":
        update.message.reply_text("You must specify a message")
        return
    # Get all groups from database
    groups = db.getAllGroups()
    # Iterate all groups
    for group in groups:
        try:
            # Send message to group id
            updater.bot.send_message(group[1], message)
            print("[MESSAGE] Message sent to group: %s" % group[1])
        except Exception as e:
            print("[ERROR] " + str(e))
            continue
    update.message.reply_text("Message sent to all groups")

    db.logEvent(update.message.from_user.id, update.message.chat.id,
                "announce", "Message sent to all groups")

def sendMessageOwner(message):
    # Send message to owner id
    updater.bot.send_message(OWNER_ID, message)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('everyone', everyone))
updater.dispatcher.add_handler(CommandHandler('all', everyone))
updater.dispatcher.add_handler(CommandHandler('in', join_list))
updater.dispatcher.add_handler(CommandHandler('out', leave_list))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('status', status))
updater.dispatcher.add_handler(CommandHandler('stats', stats))
updater.dispatcher.add_handler(CommandHandler('list', getList))
updater.dispatcher.add_handler(CommandHandler('announce', announce))

updater.dispatcher.add_handler(MessageHandler(Filters.text, everyone))

if WEB_SERVER_REPLIT == True or WEB_SERVER_REPLIT == "true":
    keep_alive()  # Replit hosting
updater.start_polling()
# On bot start, send message to owner id
if SEND_MESSAGE_OWNER == True or SEND_MESSAGE_OWNER == "true":
    # Comment this line if you don't want to send a message to the owner when the bot starts
    sendMessageOwner("✅ Bot started and ready to use")