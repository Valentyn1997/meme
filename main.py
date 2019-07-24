import argparse
from src.telegram_bot import *
from src.models import *

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='Run Telegram Bot.')
parser.add_argument('--token', help='Telegram bot token')
parser.add_argument('--mongo_address', help='Mongo DB address')

args = parser.parse_args()
if args.token is None:
    raise Exception("No Telegram Bot Token provided!")
if args.mongo_address is None:
    raise Exception("No Mongo DB address provided!")

TOKEN = args.token
MONGO_ADDRESS = args.mongo_address

model = TorchMoji()
bot = TelegramBot(token=TOKEN, mongo_adress=MONGO_ADDRESS, model=model)
bot.start_bot()

