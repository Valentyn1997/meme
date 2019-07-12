import torch
from torch.autograd import Variable
from torchmoji.model_def import TorchMoji, load_specific_weights
import numpy as np
from sklearn.model_selection import train_test_split

import torch.nn as nn
from src.data import DataGenerator
from src import TRAIN_DATASET_PATH, VA_REGRESSION_WEIGHTS_PATH, PRETRAINED_WEIGHTS_PATH

from tqdm import tqdm
import pandas as pd


class RegressionTorchMoji(TorchMoji):

    def __init__(self, weight_path, nb_tokens, final_dropout_rate=0):
        super(RegressionTorchMoji, self).__init__(nb_classes=None, nb_tokens=nb_tokens,
                                                  return_attention=True, feature_output=True)
        embedding_dim = 256
        hidden_size = 512

        # Replacing LSTM layers
        self.add_module('lstm_0', nn.LSTM(embedding_dim, hidden_size, batch_first=True, bidirectional=True))
        self.add_module('lstm_1', nn.LSTM(hidden_size * 2, hidden_size, batch_first=True, bidirectional=True))

        # Adding linear regression layer
        self.add_module('final_dropout', nn.Dropout(final_dropout_rate))
        self.add_module('output_layer', nn.Sequential(nn.Linear(self.attention_layer.attention_size, 2)))
        self.add_module('sigmoid', nn.Sigmoid())
        load_specific_weights(self, weight_path, exclude_names=['output_layer'], extend_embedding=0)

    def forward(self, input_seqs):
        return_numpy = False
        return_tensor = False
        if isinstance(input_seqs, (torch.LongTensor, torch.cuda.LongTensor)):
            input_seqs = Variable(input_seqs)
            return_tensor = True
        elif not isinstance(input_seqs, Variable):
            input_seqs = Variable(torch.from_numpy(input_seqs.astype('int64')).long())
            return_numpy = True

        # Calling torchmoji
        x, att_weights = super().forward(input_seqs)  # ATTENTION, x is tensor, so gradient doesn't propagate back !!!

        x = self.final_dropout(x)
        x = self.output_layer(x)
        outputs = self.sigmoid(x)

        # Adapt return format if needed
        if return_numpy:
            outputs = outputs.data.numpy()

        return outputs


def train():

    # Data
    data = pd.read_csv(TRAIN_DATASET_PATH)
    X, y = np.array(data.text), np.array(data[['V', 'A']])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    train_generator = DataGenerator(X_train, y_train, batch_size=64)
    test_generator = DataGenerator(X_test, y_test, batch_size=64)

    # Initialization
    num_epochs = 3
    model = RegressionTorchMoji(PRETRAINED_WEIGHTS_PATH, nb_tokens=train_generator.vocab_size, final_dropout_rate=0.5)
    inner_loss = nn.MSELoss()


    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Training

    for epoch in range(num_epochs):

        print('===========Epoch [{}/{}]============'.format(epoch + 1, num_epochs))

        for batch in tqdm(range(len(train_generator)), desc='Training'):
            X, y_true = train_generator[batch]

            input = Variable(X, requires_grad=False)
            true_output = Variable(y_true, requires_grad=False)
            model.train()  # Switching to a train mode

            # forward pass
            optimizer.zero_grad()
            output = model(input)
            loss = inner_loss(true_output, output)

            # backward
            loss.backward()
            optimizer.step()

        # log
        print(f'Loss on last train batch: {loss.data}')

        # Validation
        model.eval()
        test_loss = np.empty(len(test_generator))
        for batch in range(len(test_generator)):

            input = Variable(test_generator[batch][0], requires_grad=False)
            true_output = Variable(test_generator[batch][1], requires_grad=False)

            # forward pass
            output = model(input)
            test_loss[batch] = inner_loss(true_output, output).data

        print(f'Loss on test: {test_loss.mean()}')

    torch.save(model, VA_REGRESSION_WEIGHTS_PATH)


if __name__ == '__main__':
    train()
