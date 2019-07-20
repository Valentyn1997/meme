# meme
In this project, we introduce the concept of Multimodal Emotion Messaging Estimator (MEME), a human computation system, which is a recommender system in nature. MEME has two main objectives. Firstly, to recommend emojis on instant messaging platforms which offer recommendations of various emojis relevant to the context of the ongoing conversation between users. Secondly, creating implicit coherent massive multimodal (text, audios, images) dataset for the multimodal sentiment analysis. In this project, we are using a pretrained model for sentiment analysis with valence and arousal (VA) scores. In the text model we are concatenating n-last messages, use embeddings, bidirectional LSTM (Long short-term memory) and attention layers. Audio messages are converted to text representation and processed futher as a text message. Finally, as an output we get VA scores for the message and get emojis respective to these scores. This is how our system works.


# Installation

# Server Connection
## Ubuntu Host
* IP: 138.246.232.234
* Sudo User: meme
* Password, will be sent to your email address by yingding

