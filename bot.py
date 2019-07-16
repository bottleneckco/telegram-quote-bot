import json
import logging
from os import environ
from queue import Queue
from threading import Thread

from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from db import *

MODE = environ.get('MODE', 'dev')
TOKEN = environ['TELEGRAM_TOKEN']
CREDS = environ['GOOGLE_APPLICATION_CREDENTIALS']
URL = environ['PROD_URL']
if MODE == 'dev':
    # ngrok url
    URL = 'https://26304725.ngrok.io'

db = Db(json.loads(CREDS))

logger = logging.getLogger('quote_bot')

def start(bot, update):
    message = update.message
    update.message.reply_text('Hi, let\'s save some quotes!')
    logger.info(f'Received start msg from {message.from_user.username} in chat {message.chat.id}')


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

# def run(updater):
#     if MODE == 'prod':
#         HEROKU_APP_NAME = environ['HEROKU_APP_NAME']
#         updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
#         updater.bot.set_webhook(f'https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}')
#         logger.info('Running server on production')

#     elif MODE == 'dev':
#         updater.start_polling()
#         logger.info('Running server on development')

def setup():
    # Create bot, update queue and dispatcher instances
    bot = Bot(TOKEN)
    update_queue = Queue()
    
    dp = Dispatcher(bot, update_queue)
    
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('quote', save_quote))
    dp.add_handler(CommandHandler('random', rand_quote)) 
    
    # Start the thread
    thread = Thread(target=dp.start, name='dispatcher')
    thread.start()

    logger.info('Bot thread started')
    
    # you might want to return dispatcher as well, 
    # to stop it at server shutdown, or to register more handlers:
    # return (update_queue, dispatcher)

    return (bot, update_queue)
