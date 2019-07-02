import os
import logging
from uuid import uuid4
import numpy as np

from pymongo import MongoClient
from telegram import InlineQueryResultCachedSticker
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from src.telegram_bot.messages import MessagesLoader, MessageSaver, Chat
from src.features.audio_supporter import AudioConverter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class TelegramBot:
    MEME_CHAT_ID = -391131828
    BASIC_STICKER_SET = 'BigFaceEmoji'

    def __init__(self, token, mongo_adress, model):
        # Bot connection
        self.token = token
        self.updater = Updater(self.token, use_context=True)
        self.dp = self.updater.dispatcher
        logger.info('Bot connected.')

        # Database
        self.db = MongoClient(mongo_adress).meme
        self.db_messages_collection = self.db.messages
        self.loader = MessagesLoader(self.db_messages_collection)
        self.saver = MessageSaver(self.db_messages_collection)
        logger.info('Remote MongoDB cluster connected.')

        # Initing active chats
        self.active_chats = {}

        # Command handlers
        self.dp.add_handler(CommandHandler("start", self._start))
        self.dp.add_handler(CommandHandler("help", self._help))
        logger.info('Command handlers added.')

        # Text messages handler
        self.dp.add_handler(MessageHandler(Filters.text, self._handle_message, pass_user_data=True, pass_chat_data=True))
        logger.info('Text messages handler added.')

        # Voice messages handler
        self.dp.add_handler(MessageHandler(Filters.voice, self._handle_audio, pass_user_data=True, pass_chat_data=True))
        logger.info('Audio messages handler added.')

        # Sticker messages handler
        # self.dp.add_handler(
        #     MessageHandler(Filters.sticker, self._handle_message, pass_user_data=True, pass_chat_data=True))
        # logger.info('Sticker messages handler added.')

        # Images messages handler
        self.dp.add_handler(MessageHandler(Filters.photo, self._handle_message, pass_user_data=True, pass_chat_data=True))
        logger.info('Photo messages handler added.')

        # Inline hander
        self.dp.add_handler(InlineQueryHandler(self._inlinequery, pass_update_queue=True,
                                               pass_user_data=True, pass_chat_data=True, pass_groups=True))
        logger.info('Inline handler added.')

        # Error handler
        self.dp.add_error_handler(self._error)
        logger.info('Errors handler added.')

        # Stickers / emojis to answer
        self.stiker_set = self.updater.bot.get_sticker_set(TelegramBot.BASIC_STICKER_SET).stickers

        # ML Model
        self.model = model

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

        # Adding new chat
        if update.message.chat_id not in self.active_chats.keys():
            current_chat = Chat(chat_id=update.message.chat_id, loader=self.loader)
            self.active_chats[current_chat.chat_id] = current_chat
            logger.info(f'Chat {current_chat.chat_id} activated.')
        else:
            current_chat = self.active_chats[update.message.chat_id]

        current_chat.add_message(update.message)
        self.saver.save_one(update.message)
        TelegramBot.MEME_CHAT_ID = current_chat.chat_id

        # results = [[sticker.emoji for sticker in self.stiker_set]]
        # markup = ReplyKeyboardMarkup(results, one_time_keyboard=True, resize_keyboard=True, selective=True)

        # self.updater.bot.edit_message_reply_markup(chat_id=TelegramBot.MEME_CHAT_ID, message_id=884, reply_markup=markup)
        # self.updater.bot.send_message(chat_id=TelegramBot.MEME_CHAT_ID, text='choose:', reply_markup=markup)
        # update.message.edit_text(, )

    def _handle_audio(self, update, context):

        # Adding new chat
        if update.message.chat_id not in self.active_chats.keys():
            current_chat = Chat(chat_id=update.message.chat_id, loader=self.loader)
            self.active_chats[current_chat.chat_id] = current_chat
            logger.info(f'Chat {current_chat.chat_id} activated.')
        else:
            current_chat = self.active_chats[update.message.chat_id]

        file_id = update.message.voice.file_id
        file = self.updater.bot.get_file(file_id)

        tmp_inp = 'voice.oga'
        tmp_out = 'voice.flac'
        file.download(tmp_inp)

        AudioConverter.convert_format(tmp_inp, tmp_out)
        text_msg = AudioConverter.audio_to_text(tmp_out)

        self._delete_processed_file(tmp_inp)
        self._delete_processed_file(tmp_out)

        update.message.text = text_msg
        current_chat.add_message(update.message)
        self.saver.save_one(update.message)

    def _delete_processed_file(self, file):
        os.remove(file)
        print("Processed file removed")

    def _inlinequery(self, update, context):
        """Handle the inline query."""
        # Loading active chat info

        if TelegramBot.MEME_CHAT_ID not in self.active_chats.keys():
            # Loading history of MEME chat
            current_chat = Chat(chat_id=TelegramBot.MEME_CHAT_ID, loader=self.loader)
            self.active_chats[current_chat.chat_id] = current_chat
            logger.info(f'Chat {current_chat.chat_id} activated.')

        current_chat = self.active_chats[TelegramBot.MEME_CHAT_ID]

        # Prediction
        results_emojis = self.model.predict(current_chat.messages_queue[0]['text'])
        results_stickers = []

        # Inner join with stickerpack
        for emoji in results_emojis:
            results_stickers.extend([sticker for sticker in self.stiker_set if sticker.emoji == emoji])
        logger.info(f'Recommending {len(results_stickers)} stickers.')

        # Sending recommendation
        results = [
            InlineQueryResultCachedSticker(id=uuid4(),
                                           type='sticker',
                                           sticker_file_id=sticker.file_id)
            for sticker in results_stickers]

        update.inline_query.answer(results, cache_time=1)

    def _start(self, update, context):
        update.message.reply_text('Hello!')

    def _error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, self._error)
