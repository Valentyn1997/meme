from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))

TRAIN_DATASET_PATH = f'{ROOT_PATH}/appendix1_test.csv'
VA_REGRESSION_WEIGHTS_PATH = f'{ROOT_PATH}/models/va_regression.pt'
