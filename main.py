TOKEN = "874540228:AAEc5ucecngO_G99-zre-7AgzfFi37aBPzY"
MONGO_ADDRESS = 'mongodb+srv://meme:meme_dream_team@cluster0-ti8wf.mongodb.net/test?retryWrites=true'

from telegram_bot import *

def main():
    bot = TelegramBot(token=TOKEN, mongo_adress=MONGO_ADDRESS)
    bot.start_bot()

if __name__ == '__main__':
    main()