import pandas as pd
from sentence_tokenizer import SentenceTokenizer

if __name__== "__main__" :
    data = pd.read_csv(r'DataSetPreparation/appendix1_test.csv')
    sentences = data.text
    print('sentences:')
    print(sentences[0:10])
    st = SentenceTokenizer()
    tokens = st.tokenize_sentences(sentences)
    print('tokens:')
    print(tokens[0:10])
    # back to sentenses
    sentences = st.to_sentence(tokens)
    print('sentences:')
    print(sentences[0:10])