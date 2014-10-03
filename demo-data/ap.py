"""
Corpus preparation for VSM of the AP89 corpus.
"""
import numpy as np
import os, os.path
from StringIO import StringIO
import xml.etree.ElementTree as ET

from vsm import *
from vsm.extensions.corpusbuilders.util import word_tokenize

# parse the pseudo-xml document into a python-native dict
print "parsing ap/ap.txt"
with open('ap/ap.txt') as f:
    ap89_plain = f.read()

ap89_plain = '<DOCS>\n' + ap89_plain + '</DOCS>\n'
ap89_plain = ap89_plain.replace('&', '&#038;')
ap89_IO = StringIO(ap89_plain)
tree = ET.parse(ap89_IO)
docs = tree.getroot()

corpus = dict()
for doc in docs:
    docno = doc.find('DOCNO').text.strip()
    text = doc.find('TEXT').text.strip().replace('&#038;', '&')
    corpus[docno] = text


# Create the Corpus Object
if os.path.exists('ap.npz'):
    c = Corpus.load('ap.npz')
else:
    print "creating Corpus object"

    items = corpus.items()
    ids, docs = zip(*items)
    documents = [word_tokenize(s) for s in docs]
    corpus = sum(documents, [])
    indices = np.cumsum([len(d) for d in documents])
    del documents

    metadata = [id for id in ids]
    md_type = np.array(metadata).dtype
    dtype = [('idx', np.int), ('document_label', md_type)]
    context_data = [np.array(zip(indices, metadata), dtype=dtype)]

    c = Corpus(corpus, context_data=context_data, context_types=['document'])
    c.save('ap.npz')

print "training models"
if not os.path.exists('models'):
    os.mkdir('models')

for k in range(10,110, 10):
    m = LDA(c, 'document', K=k)
    m.train(n_iterations=20)
    m.save('models/ap89-K%d.npz' % k)
