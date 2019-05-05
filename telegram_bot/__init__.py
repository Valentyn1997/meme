import logging
from uuid import uuid4

from pymongo import MongoClient
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, InlineQueryResultCachedSticker, InlineQueryResult
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters, TypeHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram_bot.messages import MessagesLoader, MessageSaver, Chat

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class TelegramBot:

    def __init__(self, token):
        # Bot connection
        self.token = token
        self.updater = Updater(self.token, use_context=True)
        self.dp = self.updater.dispatcher
        logger.info('Bot connected.')

        # Database
        self.db = MongoClient().meme
        self.db_messages_collection = self.db.messages
        self.loader = MessagesLoader(self.db_messages_collection)
        self.saver = MessageSaver(self.db_messages_collection)

        #Initing active chats
        self.active_chats = {}

        #Command handlers
        self.dp.add_handler(CommandHandler("start", self._start))
        self.dp.add_handler(CommandHandler("help", self._help))

        # Text messages handler
        self.dp.add_handler(MessageHandler(Filters.text, self._handle_message, pass_user_data=True, pass_chat_data=True))
        logger.info('Text messages handler added.')

        #Images messages handler
        self.dp.add_handler(MessageHandler(Filters.photo, self._handle_message, pass_user_data=True, pass_chat_data=True))
        logger.info('Photo messages handler added.')

        # Inline hander
        self.dp.add_handler(InlineQueryHandler(self._inlinequery, pass_update_queue=True,
                                               pass_user_data=True, pass_chat_data=True, pass_groups=True))
        logger.info('Inline handler added.')

        # Error handler
        self.dp.add_error_handler(self._error)
        logger.info('Errors handler added.')


    def start_bot(self):
        # Start the Bot
        self.updater.start_polling()

        # Block until the user presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()
        logger.info('Bot started.')

    def _start(self, update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi!')

    def _help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')

    def _handle_message(self, update, context):

        #Adding new chat
        if update.message.chat_id not in self.active_chats.keys():
            current_chat = Chat(chat_id=update.message.chat_id, loader=self.loader)
            self.active_chats[current_chat.chat_id] = current_chat
            logger.info(f'Chat {current_chat.chat_id} activated.')
        else:
            current_chat = self.active_chats[update.message.chat_id]

        current_chat.add_message(update.message)
        self.saver.save_one(update.message)

        # emoji = getEmoji(True)

        thunderstorm = u'\U0001F4A8'  # Code: 200's, 900, 901, 902, 905
        drizzle = u'\U0001F4A7'  # Code: 300's
        rain = u'\U00002614'  # Code: 500's
        snowflake = u'\U00002744'  # Code: 600's snowflake
        snowman = u'\U000026C4'  # Code: 600's snowman, 903, 906
        atmosphere = u'\U0001F301'  # Code: 700's foogy
        clearSky = u'\U00002600'  # Code: 800 clear sky
        fewClouds = u'\U000026C5'  # Code: 801 sun behind clouds
        clouds = u'\U00002601'  # Code: 802-803-804 clouds general
        hot = u'\U0001F525'  # Code: 904
        defaultEmoji = u'\U0001F300'

        emojilist = [[thunderstorm, drizzle, rain, snowflake, snowman, atmosphere, clearSky, fewClouds, clouds, hot,
                     defaultEmoji]]

        markup = ReplyKeyboardMarkup(emojilist, one_time_keyboard=True, resize_keyboard=True, selective=True)

        update.message.reply_text('choose:', reply_markup=markup)


    def _inlinequery(self, update, context):
        """Handle the inline query."""
        # Loading active chat info

        if update.inline_query.from_user.id not in self.active_chats.keys():
            current_chat = Chat(chat_id=update.inline_query.from_user.id, loader=self.loader)
            self.active_chats[current_chat.chat_id] = current_chat
            logger.info(f'Chat {current_chat.chat_id} activated.')
        else:
            current_chat = self.active_chats[update.inline_query.from_user.id]



        results = [
            InlineQueryResultArticle(id=uuid4(),
                                     type='article',
                                     title=emoji,
                                     input_message_content=InputTextMessageContent(message_text=emoji),
                                     thumb_width=5)
            for emoji in emojilist]

        update.inline_query.answer(results, cache_time=1)

    def _start(self, update, context):
        update.message.reply_text('Hello!')

    def _error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, self._error)
