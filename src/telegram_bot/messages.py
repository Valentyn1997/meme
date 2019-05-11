from pymongo import MongoClient, ASCENDING, DESCENDING
import logging

logger = logging.getLogger(__name__)

class MessagesLoader:
    def __init__(self, messages_collection):
        self.collection = messages_collection

    def load(self, chat_id, max_messages_to_load):
        result = []
        for message in self.collection.find({"chat.id": chat_id}).sort("date", DESCENDING):
            result.append(message)
            if len(result) >= max_messages_to_load:
                break
        logger.info(f'Loaded {len(result)} messages from chat {chat_id}.')
        return result


class MessageSaver:

    def __init__(self, messages_collection):
        self.collection = messages_collection

    def save_one(self, message):
        post_id = self.collection.insert_one(message.to_dict()).inserted_id
        logger.info(f'Message {message.message_id} saved ({message.text}): {post_id}.')


class Chat:

    def __init__(self, chat_id, max_queue_size=20, loader=None):
        self.chat_id = chat_id
        self.max_queue_size = max_queue_size
        self.messages_queue = []
        if loader is not None:
            self.messages_queue = loader.load(self.chat_id, self.max_queue_size)

    def add_message(self, message):
        self.messages_queue = [message.to_dict()] + self.messages_queue
        if len(self.messages_queue) > self.max_queue_size:
            self.messages_queue.pop(-1)
        logger.info(f'Message {message.message_id} added to chat {self.chat_id}.')

    def __eq__(self, other):
        return self.chat_id == other.chat_id
