import re
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer

import warnings
warnings.filterwarnings(action='ignore', category=DeprecationWarning)

logger = logging.getLogger(__name__)

class ClassificationModel:

    def predict(expression):
        pass


class RegressionModel:

    def predict(expression):
        pass


class LogRegression (ClassificationModel):

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


