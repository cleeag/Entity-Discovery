from bs4 import BeautifulSoup
import spacy
import re
from os.path import join
import os
import numpy as np
from collections import defaultdict

data_dir = "/Users/chin/PycharmProjects/EL/data"

def classification_report(y_true, y_pred, digits=2, suffix=False):
    from seqeval.metrics.sequence_labeling import get_entities, precision_score, recall_score, f1_score
    true_entities = set(get_entities(y_true, suffix))
    pred_entities = set(get_entities(y_pred, suffix))

    name_width = 0
    d1 = defaultdict(set)
    d2 = defaultdict(set)
    for e in true_entities:
        d1[e[0]].add((e[1], e[2]))
        name_width = max(name_width, len(e[0]))
    for e in pred_entities:
        d2[e[0]].add((e[1], e[2]))

    last_line_heading = 'macro avg'
    width = max(name_width, len(last_line_heading), digits)

    headers = ["precision", "recall", "f1-score", "support"]
    head_fmt = u'{:>{width}s} ' + u' {:>9}' * len(headers)
    report = head_fmt.format(u'', *headers, width=width)
    report += u'\n\n'

    row_fmt = u'{:>{width}s} ' + u' {:>9.{digits}f}' * 3 + u' {:>9}\n'

    ps, rs, f1s, s = [], [], [], []
    for type_name, true_entities in d1.items():
        pred_entities = d2[type_name]
        nb_correct = len(true_entities & pred_entities)
        nb_pred = len(pred_entities)
        nb_true = len(true_entities)

        p = nb_correct / nb_pred if nb_pred > 0 else 0
        r = nb_correct / nb_true if nb_true > 0 else 0
        f1 = 2 * p * r / (p + r) if p + r > 0 else 0

        report += row_fmt.format(*[type_name, p, r, f1, nb_true], width=width, digits=digits)

        ps.append(p)
        rs.append(r)
        f1s.append(f1)
        s.append(nb_true)

    report += u'\n'

    # compute averages
    report += row_fmt.format('micro avg',
                             precision_score(y_true, y_pred, suffix=suffix),
                             recall_score(y_true, y_pred, suffix=suffix),
                             f1_score(y_true, y_pred, suffix=suffix),
                             np.sum(s),
                             width=width, digits=digits)
    report += row_fmt.format(last_line_heading,
                             np.average(ps, weights=s),
                             np.average(rs, weights=s),
                             np.average(f1s, weights=s),
                             np.sum(s),
                             width=width, digits=digits)

    return report


def clean_nested(q_dict: dict):
    new_dict = {}
    for key, item in q_dict.items():
        ent_span = item[1]
        ent_span.sort()
        new_item = [item[0], []]
        cur = ent_span[0]
        for i in range(1, len(ent_span)):
            if cur[1] <= ent_span[i][0]:
                new_item[1].append(cur)
                cur = ent_span[i]
            elif cur[0] == ent_span[i][0] and cur[1] < ent_span[i][1]:
                cur = ent_span[i]

        new_dict[key] = new_item
        # print(new_item[1])
    return new_dict

def bs4_parser():
    doc = """
    <DOC    id="ENG_NW_001278_20130521_F000124T2"> <DATE_TIME>2013-05-21T21:07:43</DATE_TIME> <HEADLINE> ^ent^Russia^/ent^ offers condolences to tornado-struck ^ent^U.S.^/ent^ ^ent^state^/ent^ </HEADLINE> <AUTHOR>^ent^英文雇员^/ent^</AUTHOR> <TEXT> ^ent^Russia^/ent^ offers condolences to tornado-struck ^ent^U.S.^/ent^ ^ent^state^/ent^  ^ent^MOSCOW^/ent^, May 21 (^ent^Xinhua^/ent^) -- President ^ent^Vladimir Putin^/ent^ sent his condolences to ^ent^U.S.^/ent^ President ^ent^Barack Obama^/ent^ on Tuesday over the deadly tornado that struck ^ent^Oaklahoma City^/ent^.  In his cable, ^ent^Putin^/ent^ expressed his compassion for relatives of the victims of the powerful twister, the ^ent^Kremlin^/ent^ press ^ent^service^/ent^ reported.  The tornado struck the southern suburbs of the ^ent^Oklahoma^/ent^ state ^ent^capital^/ent^ Monday afternoon, killing at least 51 people and injuring at least 140 others, officials said.  ^ent^Putin^/ent^ wished a quick recovery for those injured and stressed ^ent^Russia^/ent^'s readiness to offer disaster relief assistance.  Earlier Tuesday, the ^ent^Emergency Situations Ministry^/ent^ said it would send an aid consignment to the city if requested.  Enditem </TEXT> </DOC>"""

    soup = BeautifulSoup(doc, 'html.parser')
    print(soup)
    print(soup.find_all('text'))
    for x in soup.find_all('text'):
        # print(x)
        for c in x.contents:
            print(c)
        print()

    # all_text = soup.get_text()
    # print(all_text)
    # nlp = spacy.load('en_core_web_sm')
    # doc = nlp(all_text)
    # for sent in doc.sents:
    #     print(sent)

def test_re():
    tempt_str = """, May 
    21 (^ent^Xinhua^/ent^) -- President ^ent^Vladimir Putin^/ent^ sent his condolences to ^ent^U.S.^/ent^ President ^ent^Barack Obama^/ent^ on Tuesday over the deadly tornado that struck ^ent^Oaklahoma City^/ent^."""
    print(tempt_str)
    ents = []
    while re.search('\^ent\^', tempt_str):
        span = re.search('\^ent\^', tempt_str).span()
        tempt_str = tempt_str[:span[0]] + tempt_str[span[1]:]
        span2 = re.search('\^/ent\^', tempt_str).span()
        tempt_str = tempt_str[:span2[0]] + tempt_str[span2[1]:]
        ent = [span[0], span2[0], 'E']
        ents.append(ent)
        print(tempt_str[ent[0]:ent[1]])
    print(ents)
    print(tempt_str)

def test_json():
    import json
    f = json.load(fp=open(join("/Users/chin/PycharmProjects/EL/data", 'labeled_dict.py'), 'r'))
    for x in f:
        if " Japan's remarks on China's" in x[0]:
            print(x)
            for ent in x[1]:
                print(x[0][ent[0]:ent[1]])