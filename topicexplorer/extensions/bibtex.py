from collections import defaultdict
import ConfigParser
import os.path

import pybtex
from pybtex.database import parse_file

metadata = None

def init(viewer, config, args):
    global metadata


    try:
        filename = args.bibtex or config.get('bibtex', 'path')
    except ConfigParser.Error:
        model_path = config.get('main','path')
        filename = os.path.join(model_path, 'library.bib')

    print "Loading Bibtex metadata from", filename
    bib = parse_file(filename)

    metadata = dict()
    for entry in bib.entries:
        key = os.path.basename(bib.entries[entry].fields.get('file','').replace(':pdf',''))
        citation = pybtex.format_from_file(
            filename, style='plain', output_backend='text', citations=[entry])[3:]
        metadata[key] = citation
    

def label(doc):
    global metadata
    return metadata.get(doc,doc)
