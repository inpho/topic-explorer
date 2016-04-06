from collections import defaultdict
import os.path

import pybtex
from pybtex.database import parse_file

lda_v = None
metadata = None
context_type = None

def init(model_path, viewer, ctx_type):
    global metadata
    global lda_v
    global context_type
    filename = os.path.join(model_path, 'library.bib')
    print "Loading Bibtex metadata from", filename
    bib = parse_file('library.bib')

    metadata = dict()
    for entry in bib.entries:
        key = os.path.basename(bib.entries[entry].fields['file'].replace(':pdf',''))
        citation = pybtex.format_from_file(
            'library.bib', style='plain', output_backend='text', citations=[entry])[3:]
        metadata[key] = citation
    
    lda_v = viewer
    context_type = ctx_type

def label(doc):
    global metadata
    return metadata[doc]
