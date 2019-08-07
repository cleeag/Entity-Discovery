import argparse
import os
from os.path import join

from utils.data import Data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('task')
    input_text = parser.parse_args().task

    # input_text = 'train'
    data_dir = join(os.getcwd(), 'data')

    if input_text == "prep":
        from preprocess.preprocess import PreprocessData

        pd = PreprocessData()
        pd.build_data()
        # pd.bs_parseer()
        pd.tokenize_data(file=False)
        pd.split_data()

    elif input_text == 'train':
        from train import data_initialization, train

        data = Data()
        data.read_config(join(data_dir, 'train_config'))

        print("MODEL: train")
        data_initialization(data)
        data.generate_instance('train')
        data.generate_instance('dev')
        # data.generate_instance('test')
        # data.build_pretrain_emb()
        train(data)

    elif input_text == 'test':
        from train import load_model_decode
        data = Data()
        data.read_config(join(data_dir, 'train_config'))
        data.load(data.dset_dir)
        data.generate_instance('dev')
        decode_results, pred_scores = load_model_decode(data, 'dev')
        # if data.nbest and not data.sentence_classification:
        #     data.write_nbest_decoded_results(decode_results, pred_scores, 'raw')
        # else:
        data.write_decoded_results(decode_results, 'dev')

    elif input_text == "tok":
        from preprocess.get_tokenizer import test_tok

        test_tok()

    elif input_text == 'test':
        from preprocess.helper_functions import bs4_parser, test_re, test_json

        test_json()





