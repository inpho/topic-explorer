"""
Corpus preparation for VSM of the AP89 corpus.

Includes stoplisting based on nltk.corpus.stopwords.words('english') 
and frequency filtering <= 5.

This example can be used to help guide creation of other corpora for the 
Topic Explorer, in conjunction with the ap.ini file.
"""
import numpy as np
import os, os.path
from StringIO import StringIO
import xml.etree.ElementTree as ET

from vsm import *
from vsm.extensions.corpusbuilders.util import apply_stoplist, word_tokenize
from vsm.viewer.wrappers import doc_label_name

# parse the pseudo-xml document into a python-native dict
print "parsing ap/ap.txt"
with open('ap/ap.txt') as f:
    ap89_plain = f.read()

ap89_plain = '<DOCS>\n' + ap89_plain + '</DOCS>\n'
ap89_plain = ap89_plain.replace('&', '&#038;')
ap89_IO = StringIO(ap89_plain)
tree = ET.parse(ap89_IO)
docs = tree.getroot()

# build up a python dictionary
corpus = dict()
for doc in docs:
    docno = doc.find('DOCNO').text.strip()
    text = doc.find('TEXT').text.strip().replace('&#038;', '&')
    corpus[docno] = text


# Create the Corpus Object
corpus_path = 'ap-nltk-freq5.npz'
context_type = 'document'
if os.path.exists(corpus_path):
    c = Corpus.load(corpus_path)
else:
    print "creating Corpus object"

    # extract the data - needs a list of ids and list of lists of content
    items = corpus.items()
    ids, docs = zip(*items)

    # build the corpus
    documents = [word_tokenize(s) for s in docs]
    corpus = sum(documents, [])
    indices = np.cumsum([len(d) for d in documents])
    del documents

    # create metadata based on docids
    # NOTE: if context_type=='document':
    #           doc_label_name(context_type) == 'document_label' 
    metadata = [id for id in ids]
    md_type = np.array(metadata).dtype
    dtype = [('idx', np.int), (doc_label_name(context_type), md_type)]
    context_data = [np.array(zip(indices, metadata), dtype=dtype)]

    # build up corpus with docids and stoplist
    c = Corpus(corpus, context_data=context_data, context_types=['document'])
    c = apply_stoplist(c, nltk_stop=True, freq=5)
    c.save(corpus_path)

# train the models
print "training models"
if not os.path.exists('models'):
    os.mkdir('models')

for k in range(10,110, 10):
    m = LDA(c, 'document', K=k)
    m.train(n_iterations=20)
    m.save('models/ap-nltk-freq5-K%d.npz' % k)
