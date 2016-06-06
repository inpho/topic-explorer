import platform
#updated to use pymmseg function calls instead of plain mmseg

chinese_punctuation = [u'\u2013',
                       u'\u2014',
                       u'\u2018',
                       u'\u2019',
                       u'\u201C',
                       u'\u201D',
                       u'\u2026',
                       u'\u3001',
                       u'\u3002',
                       u'\u3008',
                       u'\u3009',
                       u'\u300A',
                       u'\u300B',
                       u'\u300C',
                       u'\u300D',
                       u'\u300E',
                       u'\u300F',
                       u'\u3010',
                       u'\u3011',
                       u'\u3014',
                       u'\u3015',
                       u'\uFF01',
                       u'\uFF08',
                       u'\uFF09',
                       u'\uFF0C',
                       u'\uFF0E',
                       u'\uFF1A',
                       u'\uFF1B',
                       u'\uFF1F',
                       u'\u250B']


if platform.system() == 'Windows':
    raise NotImplementedError("mmseg Chinese language parser not implemented for Windows systems.")
else:
    import mmseg
    import os.path
    
    TOKENIZER = None
    
    def reset_mmseg():
        global TOKENIZER
        global mmseg
        TOKENIZER = None
        reload(mmseg)
        import mmseg
    
    
    def ancient_chinese_tokenizer(raw_text):
        global TOKENIZER
        if TOKENIZER is not 'Ancient':
            # reload mmseg to re-init
            reset_mmseg()
    
            #directory of ancient dictionary
            dirname = os.path.dirname(__file__)
            dictionary = os.path.join(dirname, 'ancient words.dic')
            mmseg.dict_load_defaults()
            mmseg.Dictionary.load_words(dictionary)
            TOKENIZER = 'Ancient'
    
        # process text
        tokenizer = mmseg.Algorithm(raw_text.encode('utf-8-sig'))
        tokens = []
        for token in tokenizer:
            token = token.text.decode('utf-8-sig', errors='replace').replace(u'\x00','')
            if token:
                if token not in chinese_punctuation:
                    tokens.append(token)
    
        return tokens
    
    
    def modern_chinese_tokenizer(raw_text):
        global TOKENIZER
        if TOKENIZER is not 'Modern':
            # reload mmseg to re-init
            reset_mmseg()
    
            #directory of morden dictionary
            dirname = os.path.dirname(__file__)
            dictionary = os.path.join(dirname, 'modern words.dic')
            mmseg.dict_load_defaults()
            mmseg.dict_load_words(dictionary)
            TOKENIZER = 'Modern'
    
        # process text
        #print raw_text.encode('utf-8')
        tokenizer = mmseg.Algorithm(raw_text.encode('utf-8-sig'))
        tokens = []
        for token in tokenizer:
            token = token.text.decode('utf-8-sig', errors='replace').replace(u'\x00','')
            if token:
                tokens.append(token)
    
        return tokens
    
