import os
import logging
from uuid import uuid4
import random

from pymongo import MongoClient
from telegram import InlineQueryResultCachedSticker
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from src.telegram_bot.messages import MessagesLoader, MessageSaver, Chat
from src.features.audio_supporter import AudioConverter
from src.features.image_supporter import ImageCaptioningConverter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class TelegramBot:
    MEME_CHAT_ID = -391131828
    BASIC_STICKER_SET = 'BigFaceEmoji'
    STICKER_PACKS = {'302891759': ['animulz', 'BigFaceEmoji'], '246831753': ['BigFaceEmoji'],
                     '115944271': ['BigFaceEmoji'], '272076950': ['BigFaceEmoji'], '624961537': ['BigFaceEmoji']}

    MAX_NUMBER=10
    MAX_EMOJIS = 4

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
        self.dp.add_handler(CommandHandler("add_sticker_pack", self._add_sticker_pack))
        self.dp.add_handler(CommandHandler("delete_sticker_pack", self._delete_sticker_pack))
        self.dp.add_handler(CommandHandler("max_number_stickers", self._max_number_stickers))
        self.dp.add_handler(CommandHandler("max_number_emojis", self._max_number_emojis))
        logger.info('Command handlers added.')

        # Text messages handler
        self.dp.add_handler(MessageHandler(Filters.text, self._handle_message, pass_user_data=True, pass_chat_data=True))
        logger.info('Text messages handler added.')

        # Voice messages handler
        self.dp.add_handler(MessageHandler(Filters.voice, self._handle_audio, pass_user_data=True, pass_chat_data=True))
        self.audio_converter = AudioConverter()
        logger.info('Audio messages handler added.')

        # Image messages handler
        self.dp.add_handler(MessageHandler(Filters.photo, self._handle_image, pass_user_data=True, pass_chat_data=True))
        self.image_converter = ImageCaptioningConverter()
        logger.info('Photo messages handler added.')

        # Images messages handler
        self.dp.add_handler(MessageHandler(Filters.photo, self._handle_message, pass_user_data=True, pass_chat_data=True))
        logger.info('Photo messages handler added.')

        # Inline hander
        self.dp.add_handler(InlineQueryHandler(self._inlinequery, pass_update_queue=True,
                                               pass_user_data=True, pass_chat_data=True, pass_groups=True))
        logger.info('Inline handler added.')

        #Sticker messages handler
        self.dp.add_handler(MessageHandler(Filters.sticker, self._handle_sticker))#, pass_user_data=True, pass_chat_data=True))
        logger.info('Sticker handler added.')

        # Error handler
        self.dp.add_error_handler(self._error)
        logger.info('Errors handler added.')

        # Stickers / emojis to answer
        self.stiker_set = self.updater.bot.get_sticker_set(TelegramBot.BASIC_STICKER_SET).stickers

        self.changing_emoji=0
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
        update.message.reply_text('Hi, I am ready to make you sticker recommendations. Just add me to the group chat so I can recommend you stickers!')

    def _help(self, update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text('/start – start the MEME bot \n/help – the description of bot commands \n/add_sticker_pack – add the new sticker pack into the collection of recommendations. First send the name of the sticker pack, then call the command \n/delete_sticker_pack – delete the sticker pack from the collection. First send the name of the sticker pack, then call the command \n/max_number_stickers – set the maximum number of recommended stickers. First send the name of maximum number, then call the command \n/max_number_emojis – set the maximum number of stickers per emoji. First send the name of maximum number, then call the command')


    def _add_sticker_pack(self, update, context):
        """Send a message when the command /add_sticker_pack is issued."""
        TelegramBot.STICKER_PACKS[str(update.message.from_user['id'])].append(Chat(chat_id=update.message.chat_id, loader=self.loader).messages_queue[0]['text'])
        update.message.reply_text('The sticker pack has been added!')

    def _delete_sticker_pack(self, update, context):
        """Send a message when the command /delete_sticker_pack is issued."""
        try:
            pack = TelegramBot.STICKER_PACKS[str(update['_effective_user']['id'])]
            pack.remove(Chat(chat_id=update.message.chat_id, loader=self.loader).messages_queue[0]['text'])
            TelegramBot.STICKER_PACKS[str(update.message.from_user['id'])]=pack
            update.message.reply_text('The sticker pack has been removed!')
        except:
            update.message.reply_text('There is no such sticker pack in your collection!')

    def _max_number_stickers(self, update, context):
        """Send a message when the command /delete_sticker_pack is issued."""
        try:
            TelegramBot.MAX_NUMBER=int(Chat(chat_id=update.message.chat_id, loader=self.loader).messages_queue[0]['text'])
            update.message.reply_text('The maximum number of stickers has been specified!')
        except:
            update.message.reply_text('Use number for maximum number of stickers!')

    def _max_number_emojis(self, update, context):
        """Send a message when the command /delete_sticker_pack is issued."""
        try:
            TelegramBot.MAX_EMOJIS=int(Chat(chat_id=update.message.chat_id, loader=self.loader).messages_queue[0]['text'])
            update.message.reply_text('The maximum number of emojis has been specified!')
        except:
            update.message.reply_text('Use number for maximum number of emojis!')


    def activate_chat(self, update):
        # Adding new chat to dict of active_chats
        if update.message.chat_id not in self.active_chats.keys():
            current_chat = Chat(chat_id=update.message.chat_id, loader=self.loader)
            self.active_chats[current_chat.chat_id] = current_chat
            logger.info(f'Chat {current_chat.chat_id} activated.')
        else:  # Chat already exist
            current_chat = self.active_chats[update.message.chat_id]
        return current_chat

    def _handle_message(self, update, context):

        current_chat = self.activate_chat(update)

        # Saving message
        current_chat.add_message(update.message)
        self.saver.save_one(update.message)

        TelegramBot.MEME_CHAT_ID = current_chat.chat_id

    def _handle_audio(self, update, context):

        current_chat = self.activate_chat(update)

        # Downloading file
        file_id = update.message.voice.file_id
        file = self.updater.bot.get_file(file_id)
        tmp_index = random.random()
        tmp_inp = "voice" + str(tmp_index) + ".oga"
        tmp_out = "voice" + str(tmp_index) + ".flac"
        file.download(tmp_inp)

        # Voice to text
        self.audio_converter.convert_format(tmp_inp, tmp_out)
        text_msg = self.audio_converter.audio_to_text(tmp_out)
        update.message.text = text_msg

        # Saving message with generated text
        current_chat.add_message(update.message)
        self.saver.save_one(update.message)

        # Deleting temp files
        self._delete_processed_file(tmp_inp)
        self._delete_processed_file(tmp_out)

    def _handle_image(self, update, context):

        current_chat = self.activate_chat(update)

        # Downloading file
        file_id = update.message.photo[-1].file_id  # -1 is the biggest image
        file = self.updater.bot.get_file(file_id)
        tmp_index = random.random()
        tmp = "image" + str(tmp_index) + ".jpg"
        file.download(tmp)

        # Image to text
        text_msg = self.image_converter.image_to_text(tmp)
        update.message.text = text_msg

        # Saving message with generated text
        current_chat.add_message(update.message)
        self.saver.save_one(update.message)

        # Deleting temp files
        self._delete_processed_file(tmp)

    def _handle_sticker(self, update, context):
        if str(update['_effective_user']['id']) in TelegramBot.STICKER_PACKS.keys() and update['_effective_chat']['id'] > 0:
            TelegramBot.STICKER_PACKS[str(update.message.from_user['id'])].append(str(update.message.sticker.set_name))
            update.message.reply_text('The sticker pack has been added!')


    def _delete_processed_file(self, file):
        os.remove(file)
        # print("Processed file removed")

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

        if str(update['_effective_user']['id']) in TelegramBot.STICKER_PACKS:
            pack=TelegramBot.STICKER_PACKS[str(update['_effective_user']['id'])]
            user_packs=[]
            for i in range(len(pack)):
                user_packs.append(self.updater.bot.get_sticker_set(pack[i]).stickers)
            self.stiker_set = list(set([item for sublist in user_packs for item in sublist]))
        else:
            TelegramBot.STICKER_PACKS[str(update['_effective_user']['id'])] = TelegramBot.BASIC_STICKER_SET
            self.stiker_set = TelegramBot.BASIC_STICKER_SET



        # Inner join with stickerpack
        for emoji in results_emojis:
            stickers=[]
            i = 0
            for sticker in self.stiker_set:
                if sticker.emoji == emoji and i<TelegramBot.MAX_EMOJIS:
                    stickers.append(sticker)
                    i+=1
            results_stickers.extend(stickers)
            #results_stickers.extend([sticker for sticker in self.stiker_set if sticker.emoji == emoji])
        logger.info(f'Recommending {len(results_stickers)} stickers.')

        results_stickers=results_stickers[:TelegramBot.MAX_NUMBER]
        # Sending recommendation
        results = [
            InlineQueryResultCachedSticker(id=uuid4(),
                                           type='sticker',
                                           sticker_file_id=sticker.file_id)
            for sticker in results_stickers]

        update.inline_query.answer(results, cache_time=1)


    def _error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, self._error)
