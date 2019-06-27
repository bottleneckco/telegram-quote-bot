import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
from os import environ

from db import *

load_dotenv()
TOKEN = environ['TELEGRAM_TOKEN']
CRED_PATH = environ['GOOGLE_CRED']

db = Db(CRED_PATH)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    update.message.reply_text('Hi!')

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def save_quote(bot, update):
    message_to_quote = update.message.reply_to_message
    if message_to_quote:
        try:
            db.save_quote(message_to_quote.chat.id, message_to_quote.text, message_to_quote.from_user.username)
            update.message.reply_text('Message saved to quotes', reply_to_message_id=message_to_quote.message_id)
        except:
            update.message.reply_text('Error in server, please try again later', reply_to_message_id=message_to_quote.message_id)
            # Spit the error
    else:
        update.message.reply_text('Reply this command to the message you would like to quote')

def rand_quote(bot, update):
    # try:
    selected = db.rand_quote(update.message.chat_id)
    if not selected:
        update.message.reply_text('No quotes found')

    update.message.reply_text(f'\"{selected["msg"]}\"  by {selected["user"]}')
    # except:
    #     # Spit the error
    #     update.message.reply_text('Error in server, please try again later')

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token=TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('save', save_quote))
    dp.add_handler(CommandHandler('quote', rand_quote))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print("Running server")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    logger.info('Starting bot')
    main()
