TOKEN = "874540228:AAEc5ucecngO_G99-zre-7AgzfFi37aBPzY"

from telegram_bot import *

def main():
    bot = TelegramBot(token=TOKEN)
    bot.start_bot()

if __name__ == '__main__':
    main()