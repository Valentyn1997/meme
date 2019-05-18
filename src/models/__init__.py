import re
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
import json
import numpy as np
import emoji
from sklearn.feature_extraction.text import CountVectorizer

from torchmoji.sentence_tokenizer import SentenceTokenizer
from torchmoji.model_def import torchmoji_emojis

from torchmoji.global_variables import PRETRAINED_PATH, VOCAB_PATH

import warnings
warnings.filterwarnings(action='ignore', category=DeprecationWarning)

logger = logging.getLogger(__name__)

class ClassificationModel:

    def predict(self, expression):
        pass


class RegressionModel:

    def predict(self, expression):
        pass


class LogRegression(ClassificationModel):

    def __init__(self, path_to_model, path_to_vectorizer, path_to_encoder):
        self.model = joblib.load(path_to_model)
        self.vectorizer = joblib.load(path_to_vectorizer)
        self.encoder = joblib.load(path_to_encoder)
        self.emojis_map = {'anger': ['😡'], 'fear': ['😨'], 'joy': ['😂'], 'sadness': ['😔']}

    def _cleaning(self, expression):
        # removing @, #
        expression = re.sub(r'@\w+', '<subject>', expression)
        expression = re.sub(r'#', '', expression)

        # lower case
        expression = expression.lower()
        return expression

    def predict(self, expression):
        expression = self._cleaning(expression)
        input = self.vectorizer.transform([expression])
        output = self.model.predict(input)
        output_emotion = self.encoder.inverse_transform(output)[0]
        logger.info(f'Input: {expression}. Predicted emotion: {output_emotion}')
        return self.emojis_map[output_emotion]


class TorchMoji(ClassificationModel):

    EMOJIS = ":joy: :unamused: :weary: :sob: :heart_eyes: :pensive: :ok_hand: :blush: :heart: :smirk: :grin: :notes: :flushed: :100: :sleeping: :relieved: :relaxed: :raised_hands: :two_hearts: :expressionless: :sweat_smile: :pray: :confused: :kissing_heart: :heartbeat: :neutral_face: :information_desk_person: :disappointed: :see_no_evil: :tired_face: :v: :sunglasses: :rage: :thumbsup: :cry: :sleepy: :yum: :triumph: :hand: :mask: :clap: :eyes: :gun: :persevere: :smiling_imp: :sweat: :broken_heart: :yellow_heart: :musical_note: :speak_no_evil: :wink: :skull: :confounded: :smile: :stuck_out_tongue_winking_eye: :angry: :no_good: :muscle: :facepunch: :purple_heart: :sparkling_heart: :blue_heart: :grimacing: :sparkles:".split(' ')

    def __init__(self):
        self.maxlen = 30

        # Tokenizator
        with open(VOCAB_PATH, 'r') as f:
            self.vocabulary = json.load(f)
        self.sent_tokenizer = SentenceTokenizer(self.vocabulary, self.maxlen)

        # Model weights
        self.model = torchmoji_emojis(PRETRAINED_PATH)


    def _top_elements(self, array, k):
        ind = np.argpartition(array, -k)[-k:]
        return ind[np.argsort(array[ind])][::-1]

    def predict(self, expression, top_n=5):
        input, _, _ = self.sent_tokenizer.tokenize_sentences([expression])
        output_prob = self.model(input)[0]

        # Top emoji id
        output_emoji_ids = self._top_elements(output_prob, top_n)

        # map to emojis
        output_emojis = list(map(lambda x: self.EMOJIS[x], output_emoji_ids))
        logger.info(f'Input: {expression}. Predicted emojis: {emoji.emojize(" ".join(output_emojis), use_aliases=True)}')
        return [emoji.emojize(out, use_aliases=True) for out in output_emojis]

