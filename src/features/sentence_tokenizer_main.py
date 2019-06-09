import pandas as pd
from sentence_tokenizer import SentenceTokenizer
import json

if __name__== "__main__" :
    data = pd.read_csv(r'appendix1_test.csv')
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
    with open('vocabulary.json', 'w') as outfile:
        json.dump(st.vocabulary, outfile)
