import re

from spacy.tokenizer import Tokenizer
import spacy

puncts = """\.\,\?\!\@\#\$\%\^\&\*\<\>\(\)\:\{\}\[\]\\\|\;\/\"\'\-\’\”\“"""
# puncts = """\<\>"""


def get_tok():
    # punct_re = [r'\\' + x for x in list(puncts)]
    prefix_re = re.compile(fr"^[{puncts}]", flags=re.IGNORECASE)
    suffix_re = re.compile(fr"[{puncts}\x94]$", flags=re.IGNORECASE)
    infix_re = re.compile(fr"[{puncts}]", flags=re.IGNORECASE)
    # simple_url_re = re.compile(r'''\'s(\s|$)''', flags=re.IGNORECASE)

    nlp = spacy.load('en_core_web_sm')
    nlp.tokenizer = Tokenizer(nlp.vocab,
                 prefix_search=prefix_re.search,
                 suffix_search=suffix_re.search,
                 infix_finditer=infix_re.finditer,
                 # token_match=simple_url_re.search
                 )

    return nlp

def test_tok(org=False):
    if org:
        nlp = spacy.load('en_core_web_sm')
    else:
        nlp = get_tok()

    toker = nlp.tokenizer

    input_t = """he's is 'fjdk' fj """
    tok = [x.text for x in nlp(input_t)]
    span = [(x.idx, x.idx + len(x.text)) for x in nlp(input_t)]
    print([tup for tup in zip(tok, span)])
    while True:
        input_t = input('please input text: \n')
        tok = [x.text for x in nlp(input_t)]
        span = [(x.idx, x.idx + len(x.text)) for x in nlp(input_t)]
        print(toker.find_prefix(input_t))
        print(toker.find_suffix(input_t))
        print(toker.find_infix(input_t))
        # print(toker.token_match(input_t))
        for x in zip(tok, span):
            print(x)
        # print([tup for tup in zip(tok, span)])

if __name__ == "__main__":
    test_tok()