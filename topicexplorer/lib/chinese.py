import platform
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
            mmseg.mmseg.dict_load_defaults()
            mmseg.mmseg.dict_load_words(dictionary)
            TOKENIZER = 'Ancient'
    
        # process text
        tokenizer = mmseg.mmseg.Algorithm(raw_text.encode('utf-8-sig'))
        tokens = []
        for token in tokenizer:
            token = token.text.decode('utf-8-sig', errors='replace').replace(u'\x00','')
            if token:
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
            mmseg.mmseg.dict_load_defaults()
            mmseg.mmseg.dict_load_words(dictionary)
            TOKENIZER = 'Modern'
    
        # process text
        #print raw_text.encode('utf-8')
        tokenizer = mmseg.mmseg.Algorithm(raw_text.encode('utf-8-sig'))
        tokens = []
        for token in tokenizer:
            token = token.text.decode('utf-8-sig', errors='replace').replace(u'\x00','')
            if token:
                tokens.append(token)
    
        return tokens
    
