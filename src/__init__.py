import os
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))

PRETRAINED_VOCABULARY_SIZE = 50000

TRAIN_DATASET_PATH = f'{ROOT_PATH}/data/processed/appendix1_test.csv'
VA_REGRESSION_FOLDER = f'{ROOT_PATH}/models/text2va'
VA_REGRESSION_WEIGHTS_PATH = f'{VA_REGRESSION_FOLDER}/va_regression.pth'
VOCAB_PATH = f'{ROOT_PATH}/models/vocabulary.json'

os.makedirs(VA_REGRESSION_FOLDER, exist_ok=True)