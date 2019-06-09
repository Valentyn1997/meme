# -*- coding: utf-8 -*-
"""
Extracts lists of words from a given input in order to be used for vocabulary
generation and for tokenized datasets.
"""
import re
import unicodedata
import numpy as np
# from text_unidecode import unidecode

from tokenizer import RE_MENTION, tokenize
from filter_utils import (convert_linebreaks,
                          valid_length,
                          extract_emojis,
                          non_english_user,
                          process_word,
                          punct_word,
                          remove_variation_selectors)

MENTION_RE = re.compile(RE_MENTION)
VALID_PUNCTUATION = """.:;<=>?@`~!"#$'()+,-"""


class WordExtractor:
    """ Extracts words in Unicode format """

    def __init__(self, stream, remove_variation_selectors=True):
        self.stream = stream
        self.remove_variation_selectors = remove_variation_selectors

    def get_words(self, sentence):
        """
            Tokenizes a sentence into individual words.
            Converts Unicode into ASCII.
        """

        sentence = sentence.strip().lower()
        sentence = convert_linebreaks(sentence)

        if self.remove_variation_selectors:
            sentence = remove_variation_selectors(sentence)

        words = sentence.split()
        converted_words = []
        for w in words:
            accept_sentence, c_w = self.convert_unicode_word(w)
            if not accept_sentence:
                return []
            else:
                converted_words.append(c_w)
        sentence = ' '.join(converted_words)

        words = tokenize(sentence)
        return [process_word(w) for w in words]

    @staticmethod
    def check_ascii(word):
        """ Checks a word to be ASCII """
        try:
            word.decode('ascii')
            return True
        except (UnicodeDecodeError, AttributeError):
            return False

    # def convert_unicode_punctuation(self, word):
    #     word_converted_punct_marks = []
    #     for c in word:
    #         decoded_c = unidecode(c).lower()
    #         if len(decoded_c) == 0:
    #             word_converted_punct_marks.append(c)
    #         else:
    #             allowed_punct = punct_word(decoded_c, punct=VALID_PUNCTUATION)
    #             if allowed_punct:
    #                 word_converted_punct_marks.append(decoded_c)
    #             else:
    #                 word_converted_punct_marks.append(c)
    #     return ''.join(word_converted_punct_marks)

    def convert_unicode_word(self, word):
        """ Converts Unicode words to ASCII """
        if self.check_ascii(word):
            return True, word

        word = unicodedata.normalize("NFKC", word)
        word = self.convert_unicode_punctuation(word)

        if self.check_ascii(word):
            return True, word
        else:
            return False, ''

    def data_preprocess_filtering(self, line):
        return True, line

    def data_postprocess_filtering(self, words):
        return True, words

    def get_valid_words(self, line):
        """ Extract valid words applying different filters """

        pre_valid, pre_line = self.data_preprocess_filtering(line)
        if not pre_valid:
            return False, []

        words = self.get_words(pre_line)
        if not words:
            return False, []

        return self.data_postprocess_filtering(words)

    def convert_to_array(self):
        sentences = []
        for words in self:
            sentences.append(words)
        return sentences

    def __iter__(self):
        if self.stream is None:
            raise ValueError("Stream should be set")

        for line in self.stream:
            valid, words = self.get_valid_words(line)
            if valid and len(words):
                yield words


class MsgWordExtractor(WordExtractor):
    """ Returns array of ASCII sentences for a given msg input """

    def __init__(self, stream, wanted_emojis=None, english_words=None,
                 non_english_user_set=None,
                 ignore_url_msg=True,
                 ignore_mention_msg=False):

        self.wanted_emojis = wanted_emojis
        self.english_words = english_words
        self.non_english_user_set = non_english_user_set
        self.ignore_url_msg = ignore_url_msg
        self.ignore_mention_msg = ignore_mention_msg
        WordExtractor.__init__(self, stream)

    def validated_msg(self, data):
        """ Checks if the msg is valid """

        if self.ignore_url_msg and URLS_RE.search(data):
            return False, []

        if self.wanted_emojis is not None:
            uniq_emojis = np.unique(extract_emojis(data, self.wanted_emojis))
            if len(uniq_emojis) == 0:
                return False, []
        else:
            uniq_emojis = []

        if self.non_english_user_set is not None and non_english_user(data[1], self.non_english_user_set):
            return False, []
        return True, uniq_emojis

    def data_preprocess_filtering(self, line):
        fields = line.strip().split("\t")
        valid, emojis = self.validated_msg(fields)
        text = fields[9].replace('\\n', '') \
            .replace('\\r', '') \
            .replace('&amp', '&') if valid else ''
        return valid, text

    def data_postprocess_filtering(self, words):
        valid_length = valid_length(words, 1, None)
        if valid_length:
            return True, words
        else:
            return False, []
