import pandas as pd
from src.features.sentence_tokenizer import SentenceTokenizer
import json
from src import TRAIN_DATASET_PATH, VOCAB_PATH

if __name__ == "__main__":
    data = pd.read_csv(TRAIN_DATASET_PATH)
    sentences = data.text
    print('sentences:')
    print(sentences[0:100])
    st = SentenceTokenizer()
    tokens = st.split_train_val_test(sentences)[0]
    print('tokens:')
    print(tokens[0:100])

    # back to sentenses
    sentences = st.to_sentence(tokens)
    print('sentences:')
    print(sentences[0:100])
    with open(VOCAB_PATH, 'w') as outfile:
        json.dump(st.vocabulary, outfile)
