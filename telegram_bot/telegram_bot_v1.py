import logging
from uuid import uuid4
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import collections

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(self):
    self.updater.start_polling()


def handle_message(bot, update):
    print(update)
    print("Received", update.user_data)
    print(bot.message)
    #chat_id = update.message.chat_id
    #if update.message.text == "/start":
    #    handlers.pop(chat_id, None)
    #if chat_id in handlers:

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token="874540228:AAEc5ucecngO_G99-zre-7AgzfFi37aBPzY"
    updater = Updater(token, use_context=True)

    import telepot
    TelegramBot = telepot.Bot(token)
    print(TelegramBot.getMe())

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    print('Start')

    print(TelegramBot.getUpdates())
    #dp.add_handler(CommandHandler(
    #    'put', put, pass_user_data=True))
    #dp.add_handler(CommandHandler(
     #   'get', get, pass_user_data=True))
    #print(bot.getUpdates())
    handler = MessageHandler(Filters.text, handle_message,
                                           pass_user_data=True, pass_chat_data=True)
    dp.add_handler(handler)
    #handlers = collections.defaultdict(generator)

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    #dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(InlineQueryHandler(inlinequery))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.sticker, echo))

    # log all errors
    #dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()