import logging
from os import environ

from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update

from bot import setup

load_dotenv()
MODE = environ.get('MODE', 'dev')
TOKEN = environ['TELEGRAM_TOKEN']
# PORT = int(environ.get('PORT', '8443'))
URL = environ['PROD_URL']
if MODE == 'dev':
    # ngrok url
    URL = 'https://26304725.ngrok.io'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('quote_bot')

bot, update_queue = setup()

app = Flask(__name__)

@app.route('/hello')
def hello_world():
    return 'Hello World!'

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook_post():
    update = Update.de_json(request.get_json(force=True), bot)
    update_queue.put(update)
    return 'ok'

@app.route(f'/', methods=['GET'])
def view_quotes():
    return app.send_static_file('ui/build/index.html')
    

# Only set webhook after webhook endpoint is setup
bot.set_webhook(f'{URL}/{TOKEN}')
logger.info('Starting web server')

if __name__ == '__main__':
    app.run(threaded=True)
