import json
import re
import string
import numpy as np
from sklearn.model_selection import train_test_split
from word_extractor import WordExtractor
from create_vocab import extend_vocab, VocabBuilder


class SentenceTokenizer:
    # Create array of integers (tokens) corresponding to input sentences.

    def read_json(self):
        """read vocabulary from json file"""
        f = open("vocabulary.json")
        vocabulary = json.load(f)
        f.close()
        return vocabulary

    def __init__(self):
        self.vocabulary = self.read_json()

    def tokenize_sentences(self, sentences):
        """Converts a given list of sentences into a array of integers according to vocabulary"""
        arr_tokens = []
        for sentence in sentences:
            # take only words
            sentence = re.sub('[' + string.punctuation + ']', '', sentence).split()
            tokens = [self.vocabulary[k.lower()] if k.lower() in self.vocabulary.keys() else 'NotFound' for k in sentence]
            arr_tokens.append(tokens)
        return arr_tokens

    def to_sentence(self, arr_tokens):
        """Converts a given list of tokens into a array of words according to vocabulary"""
        # create inverse vocabulary
        vocabulary = dict((v, k) for k, v in self.vocabulary.items())
        arr_sentences = []
        for token in arr_tokens:
            sentence = [vocabulary[k] if k in vocabulary.keys() else 'NotFound' for k in token]
            arr_sentences.append(sentence)
        return arr_sentences

    def split_train_val_test(self, data, split=[0.8, 0.1, 0.1]):

        indexes = list(range(len(data)))
        ind_train, ind_test = train_test_split(indexes, test_size=split[2])
        ind_train, ind_val = train_test_split(ind_train, test_size=split[1])

        train = np.array([data[x] for x in ind_train])
        test = np.array([data[x] for x in ind_test])
        val = np.array([data[x] for x in ind_val])

        words = WordExtractor(train)
        vb = VocabBuilder(words)
        vb.count_all_words()
        self.vocabulary, added = extend_vocab(self.vocabulary, vb)
        print("Added: ", str(added))

        result = [self.tokenize_sentences(s)[0] for s in [train, val, test]]

        return result, added
