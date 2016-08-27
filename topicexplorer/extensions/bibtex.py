from collections import defaultdict
from ConfigParser import (RawConfigParser as ConfigParser,
    NoOptionError, Error as ConfigParserError)
import os.path

import pybtex
from pybtex.database import parse_file
from pybtex.exceptions import PybtexError

metadata = None


def init(app, config_file):
    global metadata
    config = ConfigParser()
    config.read(config_file)

    try:
        filename = config.get('bibtex', 'path')
    except ConfigParserError:
        model_path = config.get('main', 'path')
        filename = os.path.join(model_path, 'library.bib')

    print "Loading Bibtex metadata from", filename
    bib = parse_file(filename)

    metadata = dict()
    for entry in bib.entries:
        key = '/' + bib.entries[entry].fields.get('file', '').replace(':pdf', '')[1:]
        if 'C$\\backslash$:' in key:
            key = key.replace('C$\\backslash$:', '')
            key = key[1:]
            key = os.path.normpath(key)
        key = os.path.basename(key)
        try:
            citation = pybtex.format_from_file(
                filename, style='plain', output_backend='text', citations=[entry])[3:]
            metadata[key] = citation
        except PybtexError:
            metadata[key] = filename


def label(doc):
    global metadata
    return metadata.get(doc, doc)
