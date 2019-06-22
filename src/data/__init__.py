import json
import torch

import numpy as np

from src import VOCAB_PATH
from src.features.sentence_tokenizer import SentenceTokenizer


class DataGenerator:
    """Generates data"""

    def __init__(self, input_sentences, vad_scores, batch_size=16, maxlen=30, shuffle=True, random_state=42):
        """Initialization
        :param batch_size: size of batch
        :param shuffle: shuffle all the data after epoch end
        :param vad_scores: list of true VAD values
        """
        self.input_sentences = input_sentences
        self.batch_size = batch_size
        self.shuffle = shuffle
        if random_state is not None:
            np.random.seed(random_state)
        self.on_epoch_end()
        # self.input_shape = (self.batch_size, self.n_channels, *self.dim)
        self.vad_scores = np.array(vad_scores)
        self.maxlen = maxlen

        # Tokenizator
        with open(VOCAB_PATH, 'r') as f:
            vocabulary = json.load(f)
        self.sent_tokenizer = SentenceTokenizer(vocabulary)

    def __len__(self) -> int:
        """Denotes the number of batches per epoch"""
        return int(np.floor(len(self.input_sentences) / self.batch_size))

    def __getitem__(self, index) -> np.array:
        """Generate one batch of data"""
        if index == -1:
            index = len(self) - 1

        # Generate indexes of the batch
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]

        # Find list of IDs
        X, y = self.input_sentences[indexes], self.vad_scores[indexes]

        # Tokenize sentences
        X, _, _ = self.sent_tokenizer.tokenize_sentences(X)

        return torch.from_numpy(X.astype('int64')).long(), torch.from_numpy(y).float()

    def on_epoch_end(self):
        """Updates indexes after each epoch"""
        self.indexes = np.arange(len(self.input_sentences))
        if self.shuffle:
            np.random.shuffle(self.indexes)

