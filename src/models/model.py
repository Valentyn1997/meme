import torch
import torch.nn as nn


class EmojiModel(nn.Module):

    def __init__(self, nb_classes, nb_tokens, feature_output=False, output_logits=False,
                 embed_dropout_rate=0, final_dropout_rate=0, return_attention=False):

        super(EmojiModel, self).__init__()

        embedding_dim = 256
        hidden_size = 512
        attention_size = 4 * hidden_size + embedding_dim

        self.feature_output = feature_output
        self.embed_dropout_rate = embed_dropout_rate
        self.final_dropout_rate = final_dropout_rate
        self.return_attention = return_attention
        self.hidden_size = hidden_size
        self.output_logits = output_logits
        self.nb_classes = nb_classes

        self.add_module('embed', nn.Embedding(nb_tokens, embedding_dim))
        self.add_module('embed_dropout', nn.Dropout2d(embed_dropout_rate))
        self.add_module('lstm_0', nn.LSTM(embedding_dim, hidden_size, batch_first=True, bidirectional=True))
        self.add_module('lstm_1', nn.LSTM(hidden_size*2, hidden_size, batch_first=True, bidirectional=True))
        #self.add_module('lstm_0', LSTMHardSigmoid(embedding_dim, hidden_size, batch_first=True, bidirectional=True))
        #self.add_module('lstm_1', LSTMHardSigmoid(hidden_size*2, hidden_size, batch_first=True, bidirectional=True))
        #self.add_module('attention_layer', Attention(attention_size=attention_size, return_attention=return_attention))
        if not feature_output:
            self.add_module('final_dropout', nn.Dropout(final_dropout_rate))
            if output_logits:
                self.add_module('output_layer', nn.Sequential(nn.Linear(attention_size, nb_classes if self.nb_classes > 2 else 1)))
            else:
                self.add_module('output_layer', nn.Sequential(nn.Linear(attention_size, nb_classes if self.nb_classes > 2 else 1),
                                                              nn.Softmax() if self.nb_classes > 2 else nn.Sigmoid()))
        self.init_weights()

        self.eval()