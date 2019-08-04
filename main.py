import argparse
import os
from os.path import join

from preprocess.preprocess import PreprocessData
from preprocess.tokenizer import test_tok
from utils.data import Data
from train import data_initialization, train


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('task')
    input_text = parser.parse_args().task

    # input_text = 'train'

    if input_text == "prep":
        pd = PreprocessData()
        pd.build_data()
        # pd.bs_parseer()

        pd.tokenize_data(file=None)
        pd.split_data()

    elif input_text == 'train':
        data = Data()
        data.read_config(join(os.getcwd(), 'data/train_config'))
        print("MODEL: train")
        data_initialization(data)
        data.generate_instance('train')
        data.generate_instance('dev')
        # data.generate_instance('test')
        # data.build_pretrain_emb()
        train(data)

    elif input_text == "tok":
        test_tok()

    elif input_text == 'test':
        from preprocess.helper_functions import bs4_parser, test_re, test_json

        test_json()





