from __future__ import print_function, division
import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)


import numpy as np
import pandas as pd
import re

col_names = ['id', 'expression', 'emotion', 'score']
anger_train = pd.read_csv('http://saifmohammad.com/WebDocs/EmoInt%20Train%20Data/anger-ratings-0to1.train.txt',
                          sep='\t', header = None, names = col_names)
fear_train = pd.read_csv('http://saifmohammad.com/WebDocs/EmoInt%20Train%20Data/fear-ratings-0to1.train.txt',
                          sep='\t', header = None, names = col_names)
joy_train = pd.read_csv('http://saifmohammad.com/WebDocs/EmoInt%20Train%20Data/joy-ratings-0to1.train.txt',
                          sep='\t', header = None, names = col_names)
sadness_train = pd.read_csv('http://saifmohammad.com/WebDocs/EmoInt%20Train%20Data/sadness-ratings-0to1.train.txt',
                          sep='\t', header = None, names = col_names)
train = pd.concat([anger_train, fear_train, joy_train, sadness_train])

anger_test = pd.read_csv('http://saifmohammad.com/WebDocs/EmoInt%20Test%20Gold%20Data/anger-ratings-0to1.test.gold.txt',
                          sep='\t', header = None, names = col_names)
fear_test = pd.read_csv('http://saifmohammad.com/WebDocs/EmoInt%20Test%20Gold%20Data/fear-ratings-0to1.test.gold.txt',
                          sep='\t', header = None, names = col_names)
joy_test = pd.read_csv('http://saifmohammad.com/WebDocs/EmoInt%20Test%20Gold%20Data/joy-ratings-0to1.test.gold.txt',
                          sep='\t', header = None, names = col_names)
sadness_test = pd.read_csv('http://saifmohammad.com/WebDocs/EmoInt%20Test%20Gold%20Data/sadness-ratings-0to1.test.gold.txt',
                          sep='\t', header = None, names = col_names)
test = pd.concat([anger_test, fear_test, joy_test, sadness_test])


def cleaning(expression):
    # removing @, #
    expression = re.sub(r'@\w+', '<subject>', expression)
    expression = re.sub(r'#', '', expression)

    # lower case
    expression = expression.lower()
    return expression

train.expression = train.expression.apply(cleaning)
test.expression = test.expression.apply(cleaning)

sentences = list(train.expression) + list(test.expression)

from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(min_df=0, lowercase=True)
vectorizer.fit(sentences)
#vectorizer.vocabulary_

X_train = vectorizer.transform(list(train.expression)).toarray()
X_test = vectorizer.transform(list(test.expression)).toarray()

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
emotion_encoder = LabelEncoder()
y_train = emotion_encoder.fit_transform(train.emotion)
y_test = emotion_encoder.fit_transform(test.emotion)

# emotion_one_hot_encoder = OneHotEncoder()
# y_train = emotion_one_hot_encoder.fit_transform(y_train.reshape((-1, 1)))
# y_test = emotion_one_hot_encoder.fit_transform(y_test.reshape((-1, 1)))

from sklearn.linear_model import LogisticRegression

classifier = LogisticRegression()
classifier.fit(X_train, y_train)
score = classifier.score(X_test, y_test)

print("Accuracy:", score)

print('Telegram')
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Recommendation']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    update.message.reply_text(
        "Hi! My name is MEME. INSTRUCTIONS:1. Choose Recommendation. "
        "2. After the reply from the bot write your message. "
        "3. If you want to have a new recommendation go back to step 1.",
        reply_markup=markup)

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        text.lower())
        #'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

    return TYPING_REPLY


def custom_choice(update, context):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    print(user_data)
    print(1)
    category = user_data['choice']
    print(category)
    user_data[category] = text
    del user_data['choice']

    #print(list(user_data.values())[0])
    #print(emotion_encoder.inverse_transform(classifier.predict(vectorizer.transform([user_data])))[0])
    update.message.reply_text(emotion_encoder.inverse_transform(classifier.predict(vectorizer.transform([list(user_data.values())[0]])))[0],reply_markup=markup)
                                  #facts_to_str(emotion_encoder.inverse_transform(classifier.predict(vectorizer.transform([user_data]))))), reply_markup=markup)

    return CHOOSING


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("Recommendation".format(facts_to_str(user_data)))

    user_data.clear()
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token='874540228:AAEc5ucecngO_G99-zre-7AgzfFi37aBPzY', use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^(Recommendation)$',
                                    #emotion_encoder.inverse_transform(classifier.predict(vectorizer.transform(["bitter terrorism optimism sober"])))
                                    regular_choice,
                                    pass_user_data=True),
                       RegexHandler('^Something else...$',
                                    custom_choice),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice,
                                           pass_user_data=True),
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          #emotion_encoder.inverse_transform(classifier.predict(
                                          #    vectorizer.transform([received_information])))[0],
                                          received_information,
                                          pass_user_data=True),
                           ],
        },

        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print('Start')
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()