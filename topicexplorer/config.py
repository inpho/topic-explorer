from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

from codecs import open
from configparser import ConfigParser

def read(filename):
    config = ConfigParser({
        "htrc": False,
        "sentences": False,
        'certfile': None,
        'keyfile': None,
        'ca_certs': None,
        'ssl': False,
        'port': '8000',
        'host': '127.0.0.1',
        'icons': 'link',
        'corpus_link': None,
        'doc_title_format': '{0}',
        'doc_url_format': '',
        'raw_corpus': None,
        'label_module': None,
        'fulltext': False,
        'pdf' : False,
        'topics': None,
        'cluster': None,
        'corpus_desc' : None,
        'home_link' : '/',
        'lang' : None, 
        'tokenizer': 'default'
    })

    with open(filename, encoding='utf8') as configfile:
        config.read_file(configfile)

    return config
