import json
import re
import string

class SentenceTokenizer():
    # Create array of integers (tokens) corresponding to input sentences.


    def read_json(self):
        '''read vocabulary from json file'''
        f = open("vocabulary.json")
        vocabulary = json.load(f)
        f.close()
        return vocabulary

    def __init__(self):
        self.vocabulary = self.read_json()

    def tokenize_sentences(self, sentences):
        '''Converts a given list of sentences into a array of integers according to vocabulary'''
        arr_tokens = []
        for sentence in sentences:
            # take only words
            sentence = re.sub('['+string.punctuation+']', '', sentence).split()
            tokens = [self.vocabulary[k.lower()] if k.lower() in self.vocabulary.keys() else 'NotFound' for k in sentence]
            arr_tokens.append(tokens)
        return arr_tokens

    def to_sentence(self, arr_tokens):
        '''Converts a given list of tokens into a array of words according to vocabulary'''
        # create inverse vocabulary
        vocabulary = dict((v, k) for k, v in self.vocabulary.items())
        arr_sentences = []
        sentence = []
        for token in arr_tokens:
            sentence = [ vocabulary[k] if k in vocabulary.keys() else 'NotFound' for k in token]
            arr_sentences.append(sentence)
        return arr_sentences

