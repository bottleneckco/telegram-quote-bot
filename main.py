from os import environ
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv

from db import *

load_dotenv()
TOKEN = environ['TELEGRAM_TOKEN']
CRED_PATH = environ['GOOGLE_CRED']
MODE = environ.get('MODE', 'dev')
PORT = int(environ.get("PORT", "8443"))

db = Db(CRED_PATH)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger('quote_bot')

def start(bot, update):
    update.message.reply_text('Hi!')

# Only for telegram errors
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def save_quote(bot, update):
    message_to_quote = update.message.reply_to_message
    if message_to_quote:
        chat_id, text, username = message_to_quote.chat.id, message_to_quote.text, message_to_quote.from_user.username
        db.save_quote(chat_id, text, username)
        update.message.reply_text('Message saved to quotes', reply_to_message_id=message_to_quote.message_id)
        logger.info(f'Saved "{text}" from {username} to chat {chat_id}')
    else:
        update.message.reply_text('Reply this command to the message you would like to quote')

def rand_quote(bot, update):
    selected = db.rand_quote(update.message.chat_id)
    if not selected:
        update.message.reply_text('No quotes found')
        logger.info(f'Retrived no msg for chat {update.message.chat_id}')

    update.message.reply_text(f'"{selected["msg"]}"  by {selected["user"]}')
    logger.info(f'Retrieved random msg "{selected["msg"]}" from {selected["user"]} to chat {update.message.chat_id}')

def unknown(bot, update):
    update.message.reply_text('Sorry, I didn\'t understand that command.', reply_to_message_id=update.message.message_id)

def run(updater):
    if MODE == 'prod':
        HEROKU_APP_NAME = environ['HEROKU_APP_NAME']
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        print("Running server on prod")
    elif MODE == 'dev':
        updater.start_polling()
        print("Running server on development")

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token=TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('save', save_quote))
    dp.add_handler(CommandHandler('quote', rand_quote))
    dp.add_handler(MessageHandler(Filters.command, unknown))
    
    dp.add_error_handler(error)

    # Start the Bot
    run(updater)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    logger.info('Starting bot')
    main()
