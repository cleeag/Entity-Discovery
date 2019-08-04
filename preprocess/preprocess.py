import pandas as pd
import os
from os.path import join
import random
import re
import pickle as pkl
import json

from tqdm import tqdm
from bs4 import BeautifulSoup
import spacy
from preprocess.tokenizer import get_tok
from preprocess.helper_functions import clean_nested

def read_label():

    label_path = join(os.getcwd(), "LDC2017E52_TAC_KBP_2017_Entity_Discovery_"
                                   "and_Linking_Evaluation_Gold_Standard_Entity_Mentions_and_Knowledge_Base_Links"
                                   "/data/tac_kbp_2017_edl_evaluation_gold_standard_entity_mentions.tab")
    df = pd.read_csv(label_path, header=None, delimiter='\t')
    df = df.loc[:,[1, 2, 3]]
    df = df.rename(columns={
        1: 'entity_id',
        2: 'entity',
        3: 'doc_id'
    })
    print(df.head())
    print(df.loc[3, 'entity'])
    return df

def read_data():
    data_dir = join(os.getcwd(), "LDC2017E51_TAC_KBP_2017_Evaluation_Core_Source_Corpus/data/eng/nw")
    data_dict = {}
    for file in os.listdir(data_dir):
        with open(join(data_dir, file), 'r') as f:
            data_dict[file.split('.')[0]] = f.read()
    print(data_dict)
    return data_dict


class PreprocessData:
    def __init__(self, ):
        self.data_dir = "/Users/chin/PycharmProjects/EL/data"
        self.corpus_dir = join(self.data_dir, "LDC2017E51_TAC_KBP_2017_Evaluation_Core_Source_Corpus/data/")
        self.label_df = self._read_label()


    def build_data(self, lang='eng'):
        self.corpus = self.read_corpus(lang)
        # structure: dict
        # key: doc_id
        # value: [text, {entity_id: mention_position}]
        self.labeled_data = clean_nested(self._make_label_data_dict())
        # self.pre_tokenized_data = self.bs_parseer()



    def _read_label(self):
        label_path = join(self.data_dir, "LDC2017E52_TAC_KBP_2017_Entity_Discovery_"
                                       "and_Linking_Evaluation_Gold_Standard_Entity_Mentions_and_Knowledge_Base_Links"
                                       "/data/tac_kbp_2017_edl_evaluation_gold_standard_entity_mentions.tab")
        df = pd.read_csv(label_path, header=None, delimiter='\t')
        df = df.loc[:, [1, 2, 3]]
        df = df.rename(columns={
            1: 'entity_id',
            2: 'entity',
            3: 'doc_id'
        })
        print(df.head())
        return df

    def read_corpus(self, lang):
        data_dir = join(self.corpus_dir, f"{lang}")
        corpus_dict = {}
        for doc_type in ['df', 'nw']:
            for file in os.listdir(join(data_dir, doc_type)):
                with open(join(data_dir, doc_type, file), 'r') as f:
                    corpus_dict['.'.join(file.split('.')[:-1])] = f.read().replace('\n', ' ')
        print(len(corpus_dict))
        return corpus_dict

    def _make_label_data_dict(self):
        labeled_data = {}
        total_entities = 0
        for i in tqdm(range(len(self.label_df))):
            doc_id = self.label_df.loc[i, 'doc_id']
            if doc_id[:3] not in ['ENG', 'NYT']:
                continue
            doc_id, mention_position = doc_id.split(':')
            mention_position = [int(x) for x in mention_position.split('-')]
            mention_position[1] = mention_position[1] + 1
            total_entities += 1

            if doc_id not in labeled_data:
                labeled_data[doc_id] = [
                    self.corpus[doc_id],
                    [
                        mention_position + [self.label_df.loc[i, 'entity_id']]
                    ]
                ]
            else:
                labeled_data[doc_id][1].append(mention_position + [self.label_df.loc[i, 'entity_id']])
            labeled_data[doc_id][1].sort(key=lambda x:x[0])
        print(total_entities)
        return labeled_data

    def bs_parseer(self):
        all_sents = []
        nlp = spacy.load('en_core_web_sm')
        for doc_id, item in tqdm(self.labeled_data.items()):
            labeled_text = ''
            org_text = item[0]
            end = 0

            for ent in item[1]:
                labeled_text += org_text[end:ent[0]]
                labeled_text += f"^ent^{org_text[ent[0]:ent[1]]}^/ent^"
                end = ent[1]
            labeled_text += org_text[end:]
            # item[0] = labeled_text
            soup = BeautifulSoup(labeled_text, 'html.parser')
            for x in soup.find_all(['post', 'text']):
                for c in x.contents:
                    c = str(c)
                    if c[0] =='<':
                        continue
                    else:
                        doc = nlp(c)
                        for sent in doc.sents:
                            all_sents.append(sent.text)
                            # print(sent)
            # break
        # input('next?')
        new_labeled_dict = []
        i = 0
        while i < len(all_sents):
            sent = all_sents[i]
            tempt_str = sent
            ents = []
            while re.search('\^ent\^', tempt_str):
                span = re.search('\^ent\^', tempt_str).span()
                tempt_str = tempt_str[:span[0]] + tempt_str[span[1]:]
                if re.search('\^/ent\^', tempt_str) is None:
                    tempt_str += ' ' + all_sents[i+1]
                    i += 1
                    span2 = re.search('\^/ent\^', tempt_str).span()
                else:
                    span2 = re.search('\^/ent\^', tempt_str).span()
                tempt_str = tempt_str[:span2[0]] + tempt_str[span2[1]:]
                # print(tempt_str)
                ent = [span[0], span2[0], 'E']
                ents.append(ent)
            new_labeled_dict.append(
                [
                    tempt_str,
                    ents
                ]
            )
            i += 1
        # pkl.dump(new_labeled_dict, join(self.data_dir, 'labeled_dict.pkl'), 'w')
        json.dump(new_labeled_dict, fp=open(join(self.data_dir, 'labeled_dict.json'), 'w'), indent=4)
        return new_labeled_dict





    def tokenize_data(self, file=None):
        if file:
            labeled_data = json.load(fp=open(join(self.data_dir, 'labeled_dict.json'), 'r'))
        else:
            labeled_data = self.labeled_data
        nlp = get_tok()
        with open(join(self.data_dir, 'raw.txt'), 'w') as w:
            label_count = [0, 0]
            for item in tqdm(labeled_data):
                # print(doc_id)
                doc = nlp(item[0])

                doc_span = []
                for tok in doc:
                    doc_span.append([tok.idx, tok.idx + len(tok.text), 'O'])

                ent_span = item[1]
                all_ent_span = []
                i = 0
                while i < len(doc_span):
                    if len(ent_span) == 0:
                        all_ent_span.extend(doc_span[i:])
                        break

                    if doc_span[i][0] < ent_span[0][0]:
                        all_ent_span.append(doc_span[i])
                        i += 1
                    elif doc_span[i][0] == ent_span[0][0]:
                        if doc_span[i][1] < ent_span[0][1]:
                            j = 1
                            while i + j < len(doc_span):
                                if doc_span[i+j][1] < ent_span[0][1]:
                                    j += 1
                                elif doc_span[i+j][1] == ent_span[0][1]:
                                    i = i + j + 1
                                    break
                                elif doc_span[i+j][1] > ent_span[0][1]:
                                    print()
                                    print(doc_span[i+j], item[0][doc_span[i+j][0]:doc_span[i+j][1]])
                                    print(ent_span[0], item[0][ent_span[0][0]:ent_span[0][1]])
                                    print('wtf?')
                            # print('add ', item[0][ent_span[0][0]:ent_span[0][1]], ent_span[0])
                            all_ent_span.append(ent_span[0])
                            ent_span = ent_span[1:]
                        elif doc_span[i][1] == ent_span[0][1]:
                            ent_span[0][1] = doc_span[i][1]
                            all_ent_span.append(ent_span[0])
                            ent_span = ent_span[1:]
                            i += 1
                        else:
                            print('what the actual fuck')
                            # print(doc_id)
                            print(doc_span[i], item[0][doc_span[i][0]:doc_span[i][1]])
                            print(ent_span[0], item[0][ent_span[0][0]:ent_span[0][1]])
                            # i += 1
                            # continue


                    elif doc_span[i][0] > ent_span[0][0]:
                        print()
                        print(doc_span[i-1], item[0][doc_span[i-1][0]:doc_span[i-1][1]])
                        print(doc_span[i], item[0][doc_span[i][0]:doc_span[i][1]])
                        print(ent_span[0], item[0][ent_span[0][0]:ent_span[0][1]])
                        print('wtf???????')
                        print(all_ent_span[-1])
                        print(item[1])
                # print(label_count)


                tok_all_ent_span = []
                for ent in all_ent_span:
                    label = 'O' if ent[-1] == 'O' else 'E'
                    if label == 'E':
                        label_count[0] += 1
                    label_count[1] += 1
                    for tok in nlp(item[0][ent[0]:ent[1]]):
                        tok_all_ent_span.append([tok.idx, tok.idx+len(tok.text), label])
                        tok_str = item[0][ent[0]:ent[1]][tok.idx:tok.idx+len(tok.text)]
                        if len(tok_str.strip()) < 1:
                            continue
                        w.write('\t'.join([tok_str, label]) + '\n')
                w.write('\n')
            print(label_count)
    def split_data(self):
        with open(join(self.data_dir, 'raw.txt'), 'r') as r:
            all_data = r.readlines()

        tokenized_corpus = []
        cur = []
        for l in all_data:
            if l == '\n':
                tokenized_corpus.append(cur)
                cur = []
            else:
                cur.append(l)

        random.shuffle(tokenized_corpus)
        split = 0.8
        with open(join(self.data_dir, 'train.txt'), 'w') as w:
            for tokenized_doc in tokenized_corpus[:int(split * len(tokenized_corpus))]:
                for tok in tokenized_doc:
                    w.write(tok)
                w.write('\n')

        with open(join(self.data_dir, 'dev.txt'), 'w') as w:
            for tokenized_doc in tokenized_corpus[int(split * len(tokenized_corpus)):]:
                for tok in tokenized_doc:
                    w.write(tok)
                w.write('\n')





if __name__ == "__main__":

    d = PreprocessData()
    d.build_data()
    d.label_data()
    # d.tokenize_data()
    # d.split_data()
