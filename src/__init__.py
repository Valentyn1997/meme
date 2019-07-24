import os
from os.path import abspath, dirname, exists
import torch
from google_drive_downloader import GoogleDriveDownloader as gdd
# from src.utils import dropbox_download
import wget

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
ROOT_PATH = dirname(dirname(abspath(__file__)))

# Torchmoji
from torchmoji.global_variables import PRETRAINED_PATH as PRETRAINED_WEIGHTS_PATH
if not exists(PRETRAINED_WEIGHTS_PATH):
    os.makedirs(os.path.dirname(PRETRAINED_WEIGHTS_PATH), exist_ok=True)
    wget.download(url='https://www.dropbox.com/s/q8lax9ary32c7t9/pytorch_model.bin?dl=1',
                  out=PRETRAINED_WEIGHTS_PATH, bar=wget.bar_thermometer)
    # dropbox_download(url='https://www.dropbox.com/s/q8lax9ary32c7t9/pytorch_model.bin?dl=1',
    #                  dest_path=PRETRAINED_WEIGHTS_PATH)
TRAIN_DATASET_PATH = f'{ROOT_PATH}/data/processed/Dataset_tweets.csv'
VA_REGRESSION_WEIGHTS_PATH = f'{ROOT_PATH}/models/text2va/va_regression.pth'
VOCAB_PATH = f'{ROOT_PATH}/models/vocabulary.json'
PRETRAINED_VOCABULARY_SIZE = 50000
print(f'Torchmoji weights: {PRETRAINED_WEIGHTS_PATH}')
print(f'Torchmoji vocabulary: {VOCAB_PATH}')

# Image captioning
IMAGE_CAPTIONING_FOLDER = f'{ROOT_PATH}/models/captioning/'
os.makedirs(IMAGE_CAPTIONING_FOLDER, exist_ok=True)
IMAGE_CAPTIONING_WEIGHTS_PATH = f'{IMAGE_CAPTIONING_FOLDER}/BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth.tar'
IMAGE_CAPTIONING_WORDMAP_PATH = f'{IMAGE_CAPTIONING_FOLDER}/WORDMAP_coco_5_cap_per_img_5_min_word_freq.json'
print(f'Image captioning weights: {IMAGE_CAPTIONING_WEIGHTS_PATH}')
print(f'Image captioning word map: {IMAGE_CAPTIONING_WORDMAP_PATH}')

if not exists(IMAGE_CAPTIONING_WEIGHTS_PATH):
    print('Downloading weights for image captioning:')
    gdd.download_file_from_google_drive(file_id='1FYZ446OPEqhe-uLkgyVICjD_3-N3IZn1', showsize=True,
                                        dest_path=IMAGE_CAPTIONING_WEIGHTS_PATH, unzip=False)

if not exists(IMAGE_CAPTIONING_WORDMAP_PATH):
    print('Downloading wordmap for image captioning:')
    gdd.download_file_from_google_drive(file_id='1bt_TmTC_rUcss2MJsG_C_6DtwEttRVKc', showsize=True,
                                        dest_path=IMAGE_CAPTIONING_WORDMAP_PATH, unzip=False)
