#################################
#   Tag Everyone Telegram Bot   #
# Developed by @Non_Sono_Matteo #
#       https://matt05.ml       #
#       Github: @Matt0550       #
#################################

from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from database import Database
import json
import datetime

import os
# from keep_alive import keep_alive # Replit hosting

# Create an istance of database
db = Database()

                                   # set your owner_id and token to docker-compose.yml and start it
OWNER_ID = os.environ['owner_id']  # or insert owner id to OWNER_ID
TOKEN = os.environ['token']        # and insert token to TOKEN
                                   # and just run main.py

updater = Updater(TOKEN, use_context=True)

everyoneCommands = ["@everyone", "@all", "/everyone", "/all", "/everyone@"+updater.bot.username, "/all@"+updater.bot.username, "@"+updater.bot.username] # You can add more aliases for the command /everyone

start_time = datetime.datetime.now() # For the uptime command

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
                        update.message.reply_text("You can use this command again in %s seconds" % str(seconds - (now - last_time[user_id]).seconds))
                        # Return to avoid the function to be executed
                        return
                # Update the last time the user used the command
                last_time[user_id] = now
                # Execute the function
                func(update, context)
        return wrapper
    return decorator

@cooldown(15)
def start(update: Update, context: CallbackContext):
    # Check if bot is in a group
    if not update.message.chat.type == "group" or not update.message.chat.type == "supergroup":
        update.message.reply_text("Please add me to a group with admin permissions")
    else:
        # Check if bot is admin in the group
        if update.message.chat.get_member(updater.bot.id).status == "administrator":
            update.message.reply_text("Bot is now ready to use.\nFor more information type /help")
        else:
            update.message.reply_text("The bot must be admin to use this command in a group")

@cooldown(15)
# Function to add a member to the list
def join_list(update: Update, context: CallbackContext):
    try:
        # Get the user id and group id from the message
        user_id = update.message.from_user.id
        # Check if bot is in a group
        if update.message.chat.type == "group" or update.message.chat.type == "supergroup":
            # Remove from group id "-" and convert to int
            group_id = update.message.chat.id
            # Insert data into database
            db.insertData(group_id, user_id)
            print("[DATABASE] Inserted data into database: %s, %s" % (group_id, user_id))
            update.message.reply_text("You have been added to the list")

        else:
            update.message.reply_text("This command is can only be used in a group")
            
    except Exception as e:
        print("[ERROR] " + str(e))
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

@cooldown(15)
# Function to remove a member from the list
def leave_list(update: Update, context: CallbackContext):
    try:
        # Get the user id and group id from the message
        user_id = update.message.from_user.id
        # Check if bot is in a group
        if update.message.chat.type == "group" or update.message.chat.type == "supergroup":
            # Remove from group id "-" and convert to int
            group_id = update.message.chat.id
            # Delete data from database
            db.deleteData(group_id, user_id)
            print("[DATABAE] Deleted data from database: %s, %s" % (group_id, user_id))
            update.message.reply_text("You have been removed from the list")

        else:
            update.message.reply_text("This command is can only be used in a group")
            
    except Exception as e:
        print("[ERROR] " + str(e))
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

@cooldown(15)
def everyoneMessage(update: Update, context: CallbackContext):
    if update.message.chat.type == "group" or update.message.chat.type == "supergroup":
        # Check if bot is admin in the group
        if update.message.chat.get_member(updater.bot.id).status == "administrator":
            try: 
                # Get the group id from the message
                group_id = update.message.chat.id
                # Get data from database
                data = db.getMembers(group_id)
                # Convert data to json
                data = json.loads(data[0][0])
                # Check if data is empty
                if not data:
                    update.message.reply_text("No one is in the list")
                else:
                    # Convert data to string
                    data = str(data)
                    # Remove "[" and "]"
                    data = data.replace("[", "")
                    data = data.replace("]", "")
                    
                    members = []
                    try:
                        # Foreach data in list
                        for i in data.split(","):
                            try:
                                members.append("@" + update.message.chat.get_member(int(i)).user.username)
                            except Exception as e:
                                print("[USER] " + str(e) + " - " + str(i))
                                continue
                        # Send message with list of members
                        update.message.reply_text("\n".join(members))
                    except Exception as e:
                        print("[ERROR] " + str(e))
                        update.message.reply_text("No one is in the list")

            except Exception as e:
                print("[ERROR] " + str(e))
                # Print error with code markup
                update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")
        else:
            update.message.reply_text("The bot must be admin to use this command in a group")
    else:
        update.message.reply_text("This command is can only be used in a group")

def everyone(update: Update, context: CallbackContext):
    # Check if message contains any of the commands in the list (case insensitive)
    if any(comm in update.message.text.lower() for comm in everyoneCommands) or any(comm in update.message.text for comm in everyoneCommands):
        everyoneMessage(update, context) # Apply cooldown only if the message is in the list (command)

@cooldown(15)
def help(update: Update, context: CallbackContext):
    update.message.reply_text("""
/in - Add yourself to the Everyone's list\n
/out - Remove yourself from the Everyone's list\n
/everyone - Send a message to all in the list\n
/help - Show this message\n
/list - Show the list of everyone's list (without metion)\n
/status - Show the status of the bot\n\n
Developed by @Non_Sono_Matteo
https://matt05.ml
""")

@cooldown(15)
def getList(update: Update, context: CallbackContext):
    if update.message.chat.type == "group" or update.message.chat.type == "supergroup":
        # Check if bot is admin in the group
        if update.message.chat.get_member(updater.bot.id).status == "administrator":
            try: 
                # Get the group id from the message
                group_id = update.message.chat.id
                # Get data from database
                data = db.getMembers(group_id)
                # Convert data to json
                data = json.loads(data[0][0])
                # Check if data is empty
                if not data:
                    update.message.reply_text("No one is in the list")
                else:
                    # Convert data to string
                    data = str(data)
                    # Remove "[" and "]"
                    data = data.replace("[", "")
                    data = data.replace("]", "")
                    
                    members = []
                    try:
                        # Foreach data in list
                        for i in data.split(","):
                            try:
                                members.append(update.message.chat.get_member(int(i)).user.username + " - " + str(i))
                            except Exception as e:
                                print("[USER] " + str(e) + " - " + str(i))
                                continue
                        # Send message with list of members
                        update.message.reply_text("\n".join(members))
                    except Exception as e:
                        print("[ERROR] " + str(e))
                        update.message.reply_text("No one is in the list")

            except Exception as e:
                print("[ERROR] " + str(e))
                # Print error with code markup
                update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")
        else:
            update.message.reply_text("The bot must be admin to use this command in a group")
    else:
        update.message.reply_text("This command is can only be used in a group")

@cooldown(15)
def status(update: Update, context: CallbackContext):
    # Get the bot uptime widout microseconds
    uptime = datetime.datetime.now() - start_time
    uptime = str(uptime).split(".")[0]

    update.message.reply_text("✅ If you see this message, the bot is working\n⏰ Uptime: %s" % str(uptime))

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
updater.dispatcher.add_handler(CommandHandler('list', getList))

updater.dispatcher.add_handler(MessageHandler(Filters.text, everyone))

# keep_alive() # Replit hosting
updater.start_polling()
# On bot start, send message to owner id
sendMessageOwner("✅ Bot started and ready to use") # Comment this line if you don't want to send a message to the owner when the bot starts