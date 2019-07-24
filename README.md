# meme
In this project, we introduce the concept of Multimodal Emotion Messaging Estimator (MEME), a human computation system, which is a recommender system in nature. MEME has two main objectives. Firstly, to recommend emojis on instant messaging platforms which offer recommendations of various emojis relevant to the context of the ongoing conversation between users. Secondly, creating implicit coherent massive multimodal (text, audios, images) dataset for the multimodal sentiment analysis. In this project, we are using a pre-trained model for sentiment analysis with valence and arousal (VA) scores. In the text model we are concatenating n-last messages, use embeddings, bidirectional LSTM (Long short-term memory) and attention layers. Audio messages are converted to text representation and processed further as a text message. Finally, as an output we get VA scores for the message and get respective to these scores emojis. This is how our system works.


# General idea

By launching the project, the telegram bot MEMER (*@meme_test_bot*) will be active. The bot should be invited to a group chat in telegram in order to enable recommendations. 

# Installation

The project requires installed **python 3.6** or higher versions.


Clone the project using `git clone` or download the zip archive and unpack it.
In order to start the project run the following commands:

* Go to the project directory:

  ```cd meme```
  
* Install the requirements using python interpreter:

    ```pip install -r requirements.txt```
    
* Install **ffmpeg**:

    * On Ubuntu 
        ```sudo apt install ffmpeg```
    * On Windows
        1. Download a distributive from a [source](https://ffmpeg.zeranoe.com/builds/)
        1. Unpack
        1. Add to PATH variable



    
After successful installation of the requirements run the following command to start the bot:

``` PYTHONPATH=. python3 main.py --token=<Telegram_bot_token> --mongo_address=<MongoDB_Address>```

You can find out more about `Telegram_bot_token` and `MongoDB_Address` in the following section.

Invite the bot *@meme_test_bot* to your telegram group chat and enjoy recommendations. 



# Database and Server Connection
## Telegram Bot Token

How to set up own Telegram Bot: https://core.telegram.org/bots.

## MongoDb Address

One should create database, called `meme` with the collection `messages`. Then - `mongodb_address` is just a connection string:

![image](/uploads/7c24b7113f4181289dabd7b0c29b68f9/image.png)

## Ubuntu Host
* IP: 138.246.232.234
* Sudo User: meme
* Password, will be sent to your email address by yingding

