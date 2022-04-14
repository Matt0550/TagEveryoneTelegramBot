from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from database import Database
import json
# Create an istance of database
db = Database()
  
updater = Updater("5289537493:AAGrVK2rcpJ4OhR2wFeWc8aXyPJDMIrLe0c", use_context=True)
  
  
def start(update: Update, context: CallbackContext):
    # Check if bot is in a group
    if not update.message.chat.type == "group":
        update.message.reply_text("Please add me to a group")

  
def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)
  
def everyone(update: Update, context: CallbackContext):
    # Check if messsage is @everyone
    if update.message.text == "@everyone" or update.message.text == "@all" or update.message.text == "/everyone" or update.message.text == "/all":

        update.message.reply_text("@everyone")


def join_list(update: Update, context: CallbackContext):
    try:
        # Get the user id and group id from the message
        user_id = update.message.from_user.id
        # Check if bot is in a group
        if update.message.chat.type == "group":
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

def get_list(update: Update, context: CallbackContext):
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
            update.message.reply_text("Members in the list:\n %s" % "\n ".join(members))

    except Exception as e:
        print("[ERROR] " + str(e))
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")
  
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('everyone', everyone))
updater.dispatcher.add_handler(CommandHandler('in', join_list))
updater.dispatcher.add_handler(CommandHandler('list', get_list))

updater.dispatcher.add_handler(MessageHandler(Filters.text, everyone))


updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))  # Filters out unknown commands
  
updater.start_polling()