from mmseg import mmseg

TOKENIZER = None

def reset_mmseg():
    global TOKENIZER
    TOKENIZER = None
    reload(mmseg)
    from mmseg import mmseg


def ancient_chinese_tokenizer(raw_text):
    global TOKENIZER
    if TOKENIZER is not 'Ancient':
        # reload mmseg to re-init
        reset_mmseg()

        #directory of ancient dictionary
        dirname = os.path.dirname(__file__)
        dictionary = os.path.join(dirname, 'ancient words.dic')
        mmseg.dict_load_words(dictionary)

    # process text
    tokenizer = mmseg.Algorithm(raw_text)
    return [token for token in tokenizer]



def modern_chinese_tookenizer(raw_text):
    global MODERN_TOKENIZER
    if TOKENIZER is not 'Modern':
        # reload mmseg to re-init
        reset_mmseg()

        #directory of morden dictionary
        dirname = os.path.dirname(__file__)
        dictionary = os.path.join(dirname, 'ancient words.dic')
        mmseg.mmseg.dict_load_words(dictionary)

    # process text
    tokenizer = mmseg.Algorithm(raw_text)
    return [token for token in tokenizer]

