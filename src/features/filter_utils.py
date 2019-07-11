"""
Utils functions to process words from messages
"""
import sys
import re
import string
import emoji
from itertools import groupby
from tokenizer import RE_MENTION, RE_URL, SPECIAL_TOKENS

mention_re = re.compile(RE_MENTION)
url_re = re.compile(RE_URL)

# see https://www.utf8-chartable.de/unicode-utf8-table.pl?start=65024&utf8=string-literal
# Define different styles of emojis
VARIATION_SELECTORS = ['\ufe00',
                       '\ufe01',
                       '\ufe02',
                       '\ufe03',
                       '\ufe04',
                       '\ufe05',
                       '\ufe06',
                       '\ufe07',
                       '\ufe08',
                       '\ufe09',
                       '\ufe0a',
                       '\ufe0b',
                       '\ufe0c',
                       '\ufe0d',
                       '\ufe0e',
                       '\ufe0f']

unichr = chr
ALL_CHARS = (unichr(i) for i in range(sys.maxunicode))
CONTROL_CHARS = ''.join(map(unichr, list(range(0, 32)) + list(range(127, 160))))
CONTROL_CHAR_REGEX = re.compile('[%s]' % re.escape(CONTROL_CHARS))


def is_special_token(word):
    if word in SPECIAL_TOKENS:
        return True
    else:
        return False


def is_english(words, english, pct_eng_short=0.5, pct_eng_long=0.6, ignore_special_tokens=True, min_length=2):
    """ Checks if most words are in English """

    n_words = 0
    n_english = 0

    if english is None:
        return True, 0, 0

    for w in words:
        if len(w) < min_length or punct_word(w) or (ignore_special_tokens and is_special_token(w)):
            continue
        n_words += 1
        if w in english:
            n_english += 1

    if n_words < 2:
        return True, n_words, n_english
    if n_words < 5:
        valid_english = n_english >= n_words * pct_eng_short
    else:
        valid_english = n_english >= n_words * pct_eng_long
    return valid_english, n_words, n_english


def valid_length(words, min_words=0, max_words=99999, ignore_special_tokens=True):
    """ Ensure text contains enough English words """

    n_words = 0
    for w in words:
        if punct_word(w) or (ignore_special_tokens and is_special_token(w)):
            continue
        n_words += 1
    valid = min_words <= n_words <= max_words
    return valid


def punct_word(word, punct=string.punctuation):
    return all([True if c in punct else False for c in word])


def non_english_user(userid, non_english_user_set):
    usr = int(userid) in non_english_user_set
    return usr


def separate_emoji_and_text(text):
    emoji_chars = []
    non_emoji_chars = []
    for c in text:
        if c in emoji.UNICODE_EMOJI:
            emoji_chars.append(c)
        else:
            non_emoji_chars.append(c)
    return ''.join(emoji_chars), ''.join(non_emoji_chars)


def extract_emojis(text, target):
    text = remove_variation_selectors(text)
    return [c for c in text if c in target]


def remove_variation_selectors(text):
    """ Remove style variants, e.g. skin color """
    for var in VARIATION_SELECTORS:
        text = text.replace(var, '')
    return text


def shorten_word(word):
    """ Shorten groupings of 3+ identical consecutive chars to 2 chars """

    # only shorten ASCII words
    try:
        word.decode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError, AttributeError) as e:
        return word

    # must have at least 3 chars
    if len(word) < 3:
        return word

    # find groups of more than 2 consecutive letters
    letter_groups = [list(g) for k, g in groupby(word)]
    triple_or_more = [''.join(g) for g in letter_groups if len(g) >= 3]
    if len(triple_or_more) == 0:
        return word

    short_word = word
    for trip in triple_or_more:
        short_word = short_word.replace(trip, trip[0] * 2)

    return short_word


def detect_special_tokens(word):
    try:
        int(word)
        word = SPECIAL_TOKENS[4]
    except ValueError:
        if mention_re.findall(word):
            word = SPECIAL_TOKENS[2]
        elif url_re.findall(word):
            word = SPECIAL_TOKENS[3]
    return word


def process_word(word):
    """ Shorten and convert the word to a special token """
    word = shorten_word(word)
    word = detect_special_tokens(word)
    return word


def remove_control_chars(text):
    return CONTROL_CHAR_REGEX.sub('', text)


def convert_nonbreaking_space(text):
    for r in ['\\\\xc2', '\\xc2', '\xc2', '\\\\xa0', '\\xa0', '\xa0']:
        text = text.replace(r, ' ')
    return text


def convert_linebreaks(text):
    for r in ['\\\\n', '\\n', '\n', '\\\\r', '\\r', '\r', '<br>']:
        text = text.replace(r, ' ' + SPECIAL_TOKENS[5] + ' ')
    return text
