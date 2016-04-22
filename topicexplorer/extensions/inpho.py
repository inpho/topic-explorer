def _inpho_token_generator(document):
    from inpho.model import Session, Searchpattern
    from vsm.extensions.corpusbuilders.util import strip_punc_word, PUNC_TABLE, rehyph
    if PUNC_TABLE.get(ord('-')):
        del PUNC_TABLE[ord('-')]
    
    rest = document.lower()
    rest = rehyph(rest)
    rest = strip_punc_word(rest)
    while rest:
        first, rest = rest.split(u' ', 1)
        # always yield the raw string
        yield first
        
        # search the database for keywords
        patterns = Session.query(Searchpattern).filter(Searchpattern.searchpattern.like(first + '%')).all()
        for p in patterns:
            # check if multi-phrase starts match in the rest of the phrase.
            if u' ' in p.searchpattern:
                first_pattern_word, longpattern = p.searchpattern.split(u' ',  1)
                if first == first_pattern_word and rest.startswith(u' ' + longpattern + u' '):
                    yield u"inpho:{}".format(p.entity.ID)
            elif first == p.searchpattern:
                yield u"inpho:{}".format(p.entity.ID)

def inpho_tokenizer(document):
    return list(_inpho_token_generator(document))



