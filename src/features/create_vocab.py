# -*- coding: utf-8 -*-
from __future__ import print_function, division

import glob
import json
import uuid
from copy import deepcopy
from collections import defaultdict, OrderedDict
import numpy as np

from filter_utils import is_special_token
from word_extractor import WordExtractor
from tokenizer import SPECIAL_TOKENS

VOCAB_PATH = "path"


class VocabBuilder:
    # Create Vocabulary

    def __init__(self, generated_word):
        # initialize any new key with value of 0

        r = lambda: 0
        self.word_counts = defaultdict(r, {})
        self.word_length = 30

        for token in SPECIAL_TOKENS:

            if (len(token) < self.word_length):
                self.word_counts[token] = 0

            else:
                print("An error occurred")

        self.generated_word = generated_word

    def count_words_in_sentence(self, words):
        # generating word count
        # words: Tokenized sentence whose words should be counted.

        for word in words:
            if len(word) > 0 and len(word) <= self.word_length:
                # try: code inside the try block is executed as a normal part of the program
                try:
                    self.word_counts[word] += 1
                    # except: program's response to any exceptions in the preceding try clause.
                except KeyError:
                    self.word_counts[word] = 1

    def save_vocab(self, path=None):
        # Saves the vocabulary in a file.

        # creating the data type for the np_dict array by defining that it will contain a word

        datatype = ([('word', '|S{}'.format(self.word_length)), ('count', 'int')])
        np_dict = np.array(self.word_counts.items(), dtype=datatype)

        # sort from highest to lowest frequency
        np_dict[::-1].sort(order='count')
        data = np_dict

        if path is None:
            path = str(uuid.uuid4())

        np.savez_compressed(path, data=data)
        print("Saved dict to {}".format(path))

    def get_next_word(self):
        # Returns next tokenized sentence from the word geneerator.
        return self.generated_word.__iter__().next()

    def count_all_words(self):
        # counts for all words in all sentences of the word generator.

        for words, _ in self.generated_word:
            self.count_words_in_sentence(words)


class MasterVocab():
    # Combines vocabularies.

    def __init__(self):

        # initialize custom tokens
        self.m_vocab = {}

    def populate_master_vocab(self, vocab_path, min_words=1, f_appearance=None):
        # Populates the master vocabulary using all vocabularies found in the given path

        paths = glob.glob(vocab_path + '*.npz')
        sizes = {path: 0 for path in paths}
        dicts = {path: {} for path in paths}

        # set up and get sizes of individual dictionaries
        for path in paths:
            np_data = np.load(path)['data']

            for entry in np_data:
                word, count = entry  # What is this?
                if count < min_words:
                    continue
                if is_special_token(word):
                    continue
                dicts[path][word] = count

            sizes[path] = sum(dicts[path].values())
            print('Overall word count for {} -> {}'.format(path, sizes[path]))
            print('Overall word number for {} -> {}'.format(path, len(dicts[path])))

        vocab_of_max_size = max(sizes, key=sizes.get)
        max_size = sizes[vocab_of_max_size]
        print('Min: {}, {}, {}'.format(sizes, vocab_of_max_size, max_size))

        # can force one vocabulary to always be present
        if f_appearance is not None:
            force_appearance_path = [p for p in paths if f_appearance in p][0]
            force_appearance_vocab = deepcopy(dicts[force_appearance_path])
            print(force_appearance_path)
        else:
            force_appearance_path, force_appearance_vocab = None, None

        # normalize word counts before inserting into master dict
        for path in paths:
            normalization_factor = max_size / sizes[path]
            print('Norm factor for path {} -> {}'.format(path, normalization_factor))

            for word in dicts[path]:
                if is_special_token(word):
                    print("SPECIAL - ", word)
                    continue
                normalized_count = dicts[path][word] * normalization_factor

                # can force one vocabulary to always be present
                if force_appearance_vocab is not None:
                    try:
                        force_word_count = force_appearance_vocab[word]
                    except KeyError:
                        continue
                    # if force_word_count < 5:
                    # continue

                if word in self.m_vocab:
                    self.m_vocab[word] += normalized_count
                else:
                    self.m_vocab[word] = normalized_count

        print('Size of master_dict {}'.format(len(self.m_vocab)))
        print("Hashes for master dict: {}".format(
            len([w for w in self.m_vocab if '#' in w[0]])))

    def save_vocab(self, path_count, path_vocab, word_limit=100000):
        # Saves the master vocabulary into a file

        words = OrderedDict()
        for token in SPECIAL_TOKENS:
            # store -1 instead of np.inf, which can overflow
            words[token] = -1

        # sort words by frequency
        desc_order = OrderedDict(sorted(self.m_vocab.items(),
                                        key=lambda kv: kv[1], reverse=True))
        words.update(desc_order)

        # use encoding of up to 30 characters (no token conversions)
        # use float to store large numbers (we don't care about precision loss)
        np_vocab = np.array(words.items(), dtype=([('word', '|S30'), ('count', 'float')]))

        # output count for debugging
        counts = np_vocab[:word_limit]
        np.savez_compressed(path_count, counts=counts)

        # output the index of each word for easy lookup
        final_words = OrderedDict()
        for i, w in enumerate(words.keys()[:word_limit]):
            final_words.update({w: i})
        with open(path_vocab, 'w') as f:
            f.write(json.dumps(final_words, indent=4, separators=(',', ': ')))


def all_words_in_sentences(sentences):
    # Extracts all unique words from a given list of sentences.
    vocab = []
    if isinstance(sentences, WordExtractor):
        sentences = [s for s, _ in sentences]

    for sentence in sentences:
        for word in sentence:
            if word not in vocab:
                vocab.append(word)

    return vocab


def extend_vocab_in_file(vocab, max_tokens=10000, vocab_path=VOCAB_PATH):
    # Extends JSON-formatted vocabulary with words from vocab 

    try:
        with open(vocab_path, 'r') as f:
            current_vocab = json.load(f)
    except IOError:
        print('Vocabulary file not found, expected at ' + vocab_path)
        return

    extend_vocab(current_vocab, vocab, max_tokens)

    # Save back to file
    with open(vocab_path, 'w') as f:
        json.dump(current_vocab, f, sort_keys=True, indent=4, separators=(',', ': '))


def extend_vocab(current_vocab, new_vocab, max_tokens=10000):
    # Extends current vocabulary with words from vocab 

    words = OrderedDict()

    # sort words by frequency
    desc_order = OrderedDict(sorted(new_vocab.word_counts.items(),
                                    key=lambda kv: kv[1], reverse=True))
    words.update(desc_order)

    base_index = len(current_vocab.keys())
    added = 0
    for word in words:
        if added >= max_tokens:
            break
        if word not in current_vocab.keys():
            current_vocab[word] = base_index + added
            added += 1

    return current_vocab, added
