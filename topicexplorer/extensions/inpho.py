from __future__ import absolute_import

from inpho.model import Session, Searchpattern
from vsm.extensions.corpusbuilders.util import strip_punc_word, PUNC_TABLE, rehyph

from sqlalchemy.sql import func


def _inpho_token_generator(document):
    if PUNC_TABLE.get(ord('-')):
        del PUNC_TABLE[ord('-')]
    PUNC_TABLE[ord('\n')] = ord(' ')
    
    rest = document.lower()
    rest = rehyph(rest)
    rest = strip_punc_word(rest)
    query = Session.query(Searchpattern)

    MIN_LEN = 6 
    short_patterns = Session.query(Searchpattern.searchpattern)
    short_patterns = short_patterns.filter(func.length(Searchpattern.searchpattern) < MIN_LEN)
    short_patterns = short_patterns.distinct().all()
    short_patterns = set(w[0] for w in short_patterns)

    while rest:
        if u' ' not in rest:
            yield rest
            return

        first, rest = rest.split(u' ', 1)
        rest = rest.strip()

        # always yield the raw string
        yield first

        # check if we can simply skip the short patterns
        if len(first) < MIN_LEN and first not in short_patterns:
            continue


       
        # search the database for keywords
        patterns = query.filter(Searchpattern.searchpattern.like(first + u' %')).all()
        
        exact_match = query.filter(Searchpattern.searchpattern==first).first()
        if exact_match is not None:
            patterns.append(exact_match)

        for p in patterns:
            # check if multi-phrase starts match in the rest of the phrase.
            if u' ' in p.searchpattern:
                first_pattern_word, longpattern = p.searchpattern.split(u' ',  1)
                if first == first_pattern_word and (rest == longpattern 
			or rest.startswith(longpattern + u' ')):
                    yield u"inpho:{}".format(p.entity.ID)
            elif first == p.searchpattern:
                yield u"inpho:{}".format(p.entity.ID)


def inpho_tokenizer(document):
    return list(_inpho_token_generator(document))



