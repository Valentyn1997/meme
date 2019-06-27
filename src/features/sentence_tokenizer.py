import json
import re
import string
from sklearn.model_selection import train_test_split
import numpy as np
import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
import re
from src import VOCAB_PATH

class SentenceTokenizer:
    # Create array of integers (tokens) corresponding to input sentences.

    def read_json(self):
        """read vocabulary from json file"""
        f = open(VOCAB_PATH)
        vocabulary = json.load(f)
        f.close()
        return vocabulary

    def __init__(self, vocabulary=None):
        if vocabulary is None:
            self.vocabulary = self.lemmatize_vocab(self.read_json())
        else:
            self.vocabulary = self.lemmatize_vocab(vocabulary)

    def decontracted(phrase):
        # specific
        phrase = re.sub(r"won't", "will not", phrase)
        phrase = re.sub(r"can\'t", "can not", phrase)
        phrase = re.sub(r"could\'t", "could not", phrase)
        phrase = re.sub(r"would\'t", "would not", phrase)

        # general
        phrase = re.sub(r"n\'t", " not", phrase)
        phrase = re.sub(r"\'re", " are", phrase)
        phrase = re.sub(r"\'s", " is", phrase)
        phrase = re.sub(r"\'d", " would", phrase)
        phrase = re.sub(r"\'ll", " will", phrase)
        phrase = re.sub(r"\'t", " not", phrase)
        phrase = re.sub(r"\'ve", " have", phrase)
        phrase = re.sub(r"\'m", " am", phrase)
        return phrase

    def lemmatize_vocab(self, vocabulary):
        # exchange keys and values
        vocabulary = dict((v, k) for k, v in vocabulary.items())
        # now words are values
        lemmatizer = WordNetLemmatizer()
        lemmatized_values = [lemmatizer.lemmatize(w) for w in vocabulary.values()]
        tokens = list(range(0, len(lemmatized_values)))
        return dict(zip(lemmatized_values, tokens))

    def extend_vocabulary(self, new_word):
        # Extends current vocabulary with new words
        lemmatizer = WordNetLemmatizer()
        base_val = max(self.vocabulary.values())
        new_val = base_val + 1
        self.vocabulary[lemmatizer.lemmatize(new_word)] = new_val
        return new_val

    def save_vocabulary(self, vocabulary):

        with open(VOCAB_PATH, 'w') as outfile:
            json.dump(vocabulary, outfile)
        outfile.close()

    def tokenize_sentences(self, sentences, maxlen=30):
        """Converts a given list of sentences into a array of integers according to vocabulary"""
        sentences = ['I love mom\'s cooking',
                          'I love how you never reply back..',
                          'I love cruising with my homies',
                          'I love messing with yo mind!!',
                          'I love you and now you\'re just gone..',
                          'This is shit',
                          'This is the shit']
        tokens_matr = np.zeros((len(sentences), maxlen), dtype='uint16')
        arr_tokens = []
        i = 0
        for sentence in sentences:
            sentence = self.decontracted(sentence)
            # take only words
            sentence = re.sub('[' + string.punctuation + ']', '', sentence).split()
            tokens = [self.vocabulary[k.lower()] if k.lower() in self.vocabulary.keys() else self.extend_vocabulary(k.lower()) for k in sentence]
            for j in range(len(tokens)):
                if j<maxlen:
                    tokens_matr[i, j] = tokens[j]
            i += 1
        self.save_vocabulary(self.vocabulary)
        return tokens_matr

    def to_sentence(self, arr_tokens):
        """Converts a given list of tokens into a array of words according to vocabulary"""
        # create inverse vocabulary
        vocabulary = dict((v, k) for k, v in self.vocabulary.items())
        arr_sentences = []
        for token in arr_tokens:
            sentence = [vocabulary[k] if k in vocabulary.keys() else 'NotFound' for k in token]
            arr_sentences.append(sentence)
        return arr_sentences

    def split_train_val_test(self, data, split=[0.8, 0.1, 0.1], extend_with=0):

        indexes = list(range(len(data)))
        ind_train, ind_test = train_test_split(indexes, test_size=split[2])
        ind_train, ind_val = train_test_split(ind_train, test_size=split[1])

        train = [data[x] for x in ind_train]
        test = [data[x] for x in ind_test]
        val = [data[x] for x in ind_val]

        result = [self.tokenize_sentences(s) for s in [train, val, test]]

        return result



