import pandas as pd
from sentence_tokenizer import SentenceTokenizer
import json

if __name__== "__main__" :
    data = pd.read_csv(r'appendix1_test.csv')
    sentences = data.text
    print('sentences:')
    print(sentences[0:10])
    st = SentenceTokenizer()
    tokens = st.split_train_val_test(sentences)
    print('tokens:')
    print(tokens[0][0:10])
    # back to sentenses
    sentences = st.to_sentence(tokens[0])
    print('sentences:')
    print(sentences[0:10])
    with open('data.json', 'w') as outfile:
        json.dump(st.vocabulary, outfile)
