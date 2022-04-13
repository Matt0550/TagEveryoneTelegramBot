from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from database import Database

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
            print(user_id, group_id)
            # Insert data into database
            db.insertData(group_id, user_id)
            # print(db.getMembers(group_id))
            # db.closeConnection()
            update.message.reply_text("You have been added to the list")

        else:
            update.message.reply_text("Please add me to a group")
            
    except Exception as e:
        print(e)
        # Print error with code markup
        update.message.reply_text("Error:\n`%s`" % e, parse_mode="Markdown")

  
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('everyone', everyone))
updater.dispatcher.add_handler(CommandHandler('in', join_list))

updater.dispatcher.add_handler(MessageHandler(Filters.text, everyone))


updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))  # Filters out unknown commands
  
updater.start_polling()