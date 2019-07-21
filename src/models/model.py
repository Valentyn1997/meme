import torch
from torch.autograd import Variable
from torchmoji.model_def import TorchMoji, load_specific_weights
import numpy as np
from sklearn.model_selection import train_test_split

import torch.nn as nn
from torchmoji.global_variables import PRETRAINED_PATH
from src.data import DataGenerator
from src import TRAIN_DATASET_PATH, VA_REGRESSION_WEIGHTS_PATH, PRETRAINED_VOCABULARY_SIZE
from src.models.attlayer import Attention

from tqdm import tqdm
import pandas as pd


class RegressionTorchMoji(TorchMoji):

    def __init__(self, weight_path, nb_tokens, device, final_dropout_rate=0.):
        super(RegressionTorchMoji, self).__init__(nb_classes=None, nb_tokens=nb_tokens, feature_output=True, return_attention=True)

        self.device = device
        embedding_dim = 256
        hidden_size = 512

        attention_size = 4 * hidden_size + embedding_dim
        fc_size = 4 * hidden_size + embedding_dim

        # Replacing LSTM layers and attention
        self.add_module('lstm_0', nn.LSTM(embedding_dim, hidden_size, batch_first=True, bidirectional=True))
        self.add_module('lstm_1', nn.LSTM(hidden_size * 2, hidden_size, batch_first=True, bidirectional=True))
        self.add_module('attention_layer', Attention(attention_size=attention_size, return_attention=True, device=device))

        # Adding linear regression layer
        self.add_module('fc_layer', nn.Linear(self.attention_layer.attention_size, fc_size))
        self.add_module('fc_dropout', nn.Dropout(final_dropout_rate))
        self.add_module('output_layer', nn.Linear(fc_size, 2))
        self.add_module('final_dropout', nn.Dropout(final_dropout_rate))
        self.add_module('sigmoid', nn.Sigmoid())
        load_specific_weights(self, weight_path, exclude_names=['output_layer'], extend_embedding=0)

    def forward(self, input_seqs, return_numpy=False):
        if isinstance(input_seqs, (torch.LongTensor, torch.cuda.LongTensor)):
            input_seqs = Variable(input_seqs).to(self.device)
        elif isinstance(input_seqs, Variable):
            input_seqs = input_seqs.to(self.device)
        elif isinstance(input_seqs, np.array):
            input_seqs = Variable(torch.from_numpy(input_seqs.astype('int64')).long()).to(self.device)
            return_numpy = True

        # Calling torchmoji
        x, att_weights = super().forward(input_seqs)  # ATTENTION, x is tensor, so gradient doesn't propagate back !!!

        # x = self.final_dropout(x)
        # x = self.fc_layer(x)
        # x = nn.ReLU()(x)
        x = self.final_dropout(x)
        x = self.output_layer(x)
        x = self.sigmoid(x)

        outputs = x
        # Adapt return format if needed
        if return_numpy:
            outputs = outputs.cpu().data.numpy()

        return outputs


def train():

    # Data
    data = pd.read_csv(TRAIN_DATASET_PATH)
    data = data.dropna()
    X, y = np.array(data.Tweet), np.array(data[['V', 'A']])
    print(y.min(), y.max())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    train_generator = DataGenerator(X_train, y_train, batch_size=64)
    test_generator = DataGenerator(X_test, y_test, batch_size=64)

    # Initialization
    num_epochs = 300
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f'Available device: {device}')
    model = RegressionTorchMoji(PRETRAINED_PATH,
                                nb_tokens=PRETRAINED_VOCABULARY_SIZE,
                                final_dropout_rate=0.5, device=device).to(device)
    inner_loss = nn.MSELoss()
    outer_loss = nn.MSELoss()

    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)

    # Training

    for epoch in range(num_epochs):

        print('===========Epoch [{}/{}]============'.format(epoch + 1, num_epochs))

        for batch in tqdm(range(len(train_generator)), desc='Training'):
            X, y_true = train_generator[batch]

            input = Variable(X).to(device)
            true_output = Variable(y_true).to(device)
            model.train()  # Switching to a train mode

            # forward pass
            optimizer.zero_grad()
            output = model(input)
            loss = inner_loss(output, true_output)

            # backward
            loss.backward()
            optimizer.step()

        # log
        print(f'Loss on last train batch: {loss.data}')

        # Validation
        model.eval()
        test_loss = np.empty(len(test_generator))
        for batch in range(len(test_generator)):

            input = Variable(test_generator[batch][0], requires_grad=False).to(device)
            true_output = Variable(test_generator[batch][1], requires_grad=False).to(device)

            # forward pass
            output = model(input)
            test_loss[batch] = outer_loss(true_output, output).data

        print(f'Loss on test: {test_loss.mean()}')

    torch.save(model, VA_REGRESSION_WEIGHTS_PATH)


if __name__ == '__main__':
    train()
