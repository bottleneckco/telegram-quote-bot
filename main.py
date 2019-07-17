import logging
import json

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
from os import environ
from db import *

load_dotenv()
TOKEN = environ['TELEGRAM_TOKEN']
CREDS = environ['GOOGLE_APPLICATION_CREDENTIALS']
MODE = environ.get('MODE', 'dev')
PORT = int(environ.get('PORT', '8443'))

db = Db(json.loads(CREDS))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('quote_bot')

def start(bot, update):
    update.message.reply_text('Hi, let\'s save some quotes!')

# Only for telegram errors
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def save_quote(bot, update):
    message_to_quote = update.message.reply_to_message

    if message_to_quote:
        if message_to_quote.text:
            chat_id = message_to_quote.chat.id
            username = message_to_quote.from_user.username
            text, datetime = message_to_quote.text, message_to_quote.date
            
            db.save_quote(chat_id, text, username, datetime)
            update.message.reply_text('Message saved to quotes', reply_to_message_id=message_to_quote.message_id)
            logger.info(f'Saved "{text}" from {username} to chat {chat_id}')

        else:
            update.message.reply_text('Sorry, you can only save text messages.')

    else:
        update.message.reply_text('Reply this command to the message you would like to quote.')

def rand_quote(bot, update):
    quote = db.rand_quote(update.message.chat_id)

    if not quote:
        update.message.reply_text('No quotes yet. Trying saving some quotes!')
        logger.info(f'Retrieved no msg for chat {update.message.chat_id}')

    else:
        date = quote["datetime"].strftime('%d/%m/%Y')
        update.message.reply_text(f'"{quote["msg"]}" \u2014 @{quote["user"]} on {date}')
        logger.info(f'Retrieved random msg "{quote["msg"]}" from {quote["user"]} to chat {update.message.chat_id}')

def send_link(bot, update):
    URL = 'https://quote-bot.netlify.com/'
    update.message.reply_text(f'View and manage your quotes at: \n{URL}{update.message.chat_id}')
    logger.info(f'Sent link for {update.message.chat_id}')

def run(updater):
    if MODE == 'prod':
        HEROKU_APP_NAME = environ['HEROKU_APP_NAME']
        updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
        updater.bot.set_webhook(f'https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}')
        logger.info('Running server on production')

    elif MODE == 'dev':
        updater.start_polling()
        logger.info('Running server on development')

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token=TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('quote', save_quote))
    dp.add_handler(CommandHandler('random', rand_quote))
    dp.add_handler(CommandHandler('link', send_link))
    
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
