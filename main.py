import logging
from os import environ

from flask import Flask
from dotenv import load_dotenv

from bot import setup

load_dotenv()
MODE = environ.get('MODE', 'dev')
PORT = int(environ.get('PORT', '8443'))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('quote_bot')

update_queue, dispatcher = setup()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

logger.info('Starting web server')
