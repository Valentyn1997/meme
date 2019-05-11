TOKEN = "874540228:AAEc5ucecngO_G99-zre-7AgzfFi37aBPzY"
MONGO_ADDRESS = 'mongodb+srv://meme:meme_dream_team@cluster0-ti8wf.mongodb.net/test?retryWrites=true'

from src.telegram_bot import *
from src.models import *

def main():
    model = LogRegression(path_to_model=r'models\logistic_regression\log_regression_0.81.model',
                          path_to_vectorizer=r'models\logistic_regression\vectorizer.vec',
                          path_to_encoder=r'models\logistic_regression\emotion_encoder.enc')
    bot = TelegramBot(token=TOKEN, mongo_adress=MONGO_ADDRESS, model=model)
    bot.start_bot()

if __name__ == '__main__':
    main()