from setuptools import find_packages, setup

setup(
    name='src',
    packages=find_packages(),
    version='0.1.0',
    description='The conversations, or chats, taking place using message apps often convey different emotions. Such emotions are sometime expressed through emojis. Emojis can be considered as an implicit label of the emotion expressed in a conversation. The participants of this project will collect texts from the conversations of a messaging app, such as telegram messenger, using some of these texts, train a supervised ML model which recommends emojis as emotion-conveying labels for conversations. If possible, the fitness of the emoji-recommender should be tested using part of the texts collected.',
    author='meme_team_hca',
    license='MIT',
)
