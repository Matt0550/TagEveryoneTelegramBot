from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from database import Database
import json
import random
# from keep_alive import keep_alive

# Create an istance of database
db = Database()
  
updater = Updater("INSERT_TOKEN_HERE", use_context=True)
  
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

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)

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
            print("[DATABAE] Inserted data into database: %s, %s" % (group_id, user_id))
            update.message.reply_text("You have been added to the list")

        else:
            update.message.reply_text("This command is can only be used in a group")
            
    except Exception as e:
        print("[ERROR] " + str(e))
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

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

words = ["gg", "cc", "gaddean", "gaddean bro", "gg bro", "cc bro"]
def everyone(update: Update, context: CallbackContext):
    # Check if message contains a word from the list
    if any(word in update.message.text.lower() for word in words):
        # Random response from words list
        update.message.reply_text(words[random.randint(0, len(words) - 1)])
    
    if update.message.text == "@everyone" or update.message.text == "@all" or update.message.text == "/everyone" or update.message.text == "/all" or update.message.text == "@"+update.message.bot.username:
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
                    # Print error with code markup
                    update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")
            else:
                update.message.reply_text("The bot must be admin to use this command in a group")
        else:
            update.message.reply_text("This command is can only be used in a group")

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('everyone', everyone))
updater.dispatcher.add_handler(CommandHandler('all', everyone))
updater.dispatcher.add_handler(CommandHandler('in', join_list))
updater.dispatcher.add_handler(CommandHandler('out', leave_list))

updater.dispatcher.add_handler(MessageHandler(Filters.text, everyone))

updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))  # Filters out unknown commands

# keep_alive() # Replit hosting
updater.start_polling()