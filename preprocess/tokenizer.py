import re

from spacy.tokenizer import Tokenizer
import spacy

puncts = """\.\,\?\!\@\#\$\%\^\&\*\<\>\(\)\:\{\}\[\]\\\|\;\/\"\'\-\’\”\“"""
# puncts = """\<\>"""

ss = """\(\)\:\{\}\[\]\\\|\;"""

def get_tok():
    # punct_re = [r'\\' + x for x in list(puncts)]
    prefix_re = re.compile(fr"^[{puncts}]", flags=re.IGNORECASE)
    suffix_re = re.compile(fr"[{puncts}\x94]$", flags=re.IGNORECASE)
    infix_re = re.compile(fr"[{puncts}]", flags=re.IGNORECASE)
    # simple_url_re = re.compile(r'''^https?://''')

    nlp = spacy.load('en_core_web_sm')
    tok = Tokenizer(nlp.vocab,
                 prefix_search=prefix_re.search,
                 suffix_search=suffix_re.search,
                 infix_finditer=infix_re.finditer
                 # token_match=simple_url_re.match
                 )

    return tok

def test_tok():
    nlp = get_tok()
#     input_t = """<DOC    id="ENG_NW_001278_20131125_F000134SK">
# <DATE_TIME>2013-11-25T04:39:04</DATE_TIME>
# <HEADLINE>
# Japan's remarks on China's air defense identification zone "unacceptable": DM spokesman
# </HEADLINE>
# <AUTHOR>钱彤２ 左元峰</AUTHOR>
# <TEXT>
# Japan's remarks on China's air defense identification zone "unacceptable": DM spokesman
#
# BEIJING, Nov. 24 (Xinhua) -- China's Ministry of National Defense on Sunday called Japan's remarks on the Diaoyu Islands included in the East China Sea Air Defense Identification Zone "absolutely groundless and unacceptable."
#
# The ministry's spokesman Yang Yujun said that China had explained its policy stance on the issue in various ways following its announcement of the setup of the East China Sea Air Defense Identification Zone on Saturday, and Japan's remarks are "utterly groundless and China won't accept them."
#
# Yang made the remarks while responding to questions concerning the Japanese government saying that it couldn't accept the fact that the zone covered the Diaoyu Islands.
#
# According to Yang, the foreign affairs office under the ministry lodged solemn representations with the Japanese Embassy in China.
#
# Yang reiterated that China's move aims to safeguard the country's state sovereignty and territorial and airspace safety and ensure the order for flight.
#
# Yang said the move is a necessary measure for China to effectively exercise the self-defense right and conforms to the Charter of the United Nations and international laws and practices.
#
# Having established its own air defense identification zone in late 1960s, Japan has no right to make irresponsible remarks on China's setup of the East China Sea Air Defense Identification Zone, Yang said.
#
# According to Yang, Japan has frequently sent military planes in recent years to track and monitor Chinese military planes which were conducting normal exercises and patrols above the East China Sea in the name of entering its own air defense identification zone, which severely undermined the freedom of over-flight and made safety accidents and unexpected incidents highly likely.
#
# Yang also accused the Japanese officials of using the media to maliciously report about China's legal and normal flights in an attempt to confound public opinions and create oppositional emotions.
#
# "Facts have proven that it is Japan who has been creating tense situations," Yang said.
#
# Yang stressed that the Diaoyu Islands are an inherent part of China's territory, and the country's determination and volition to safeguard its sovereignty over the islands are "unwavering."
#
# "We strongly require the Japanese side to stop all moves that undermine China's territorial sovereignty as well as irresponsible remarks that misguide international opinions and create regional tensions," Yang said.
#
# At the same day, Yang also made remarks over U.S. Department of Defence's so-called "concern" over the issue.
#
# The Foreign Affairs Office of China's Defense Ministry has lodged solemn representations with the military attache of the U.S. Embassy in China Sunday evening, Yang said.
#
# The establishment of the East China Sea Air Defense Identification Zone by the Chinese government is "totally rational and indisputable," he stressed.
#
# According to Yang, 20-plus countries, including the United States, have set up their own air defense identification zones since the 1950s.
#
# "The United States now raised to China blame and even opposition, which is totally groundless," he said.
#
# "The current situation over the Diaoyu Islands was completely caused by the wrong words and deeds of the Japanese side," he said, adding that the United States "should not choose side" over the issue and "make no more inappropriate remarks or send no wrong signal that may lead to the risky move by Japan."
#
# "We demand the U.S. side to earnestly respect China's national security,stop making irresponsible remarks for China's setup of the East China Sea Air Defense Identification Zone and make concrete efforts for the peace and stability in the Asia-Pacific region," Yang said.  Enditem
# </TEXT>
# </DOC>
# """
    input_t = """<AUTHOR>英文雇员</AUTHOR>"""
    tok = [x.text for x in nlp(input_t)]
    span = [(x.idx, x.idx + len(x.text)) for x in nlp(input_t)]
    print([tup for tup in zip(tok, span)])
    while True:
        input_t = input('please input text: \n')
        tok = [x.text for x in nlp(input_t)]
        span = [(x.idx, x.idx + len(x.text)) for x in nlp(input_t)]
        print(nlp.find_prefix(input_t))
        print(nlp.find_suffix(input_t))
        print(nlp.find_infix(input_t))
        print([tup for tup in zip(tok, span)])

if __name__ == "__main__":
    test_tok()