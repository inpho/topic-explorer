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
import tarfile
import xml.etree.ElementTree as ET

import wget

from vsm import *
from vsm.extensions.corpusbuilders.util import apply_stoplist, word_tokenize
from vsm.viewer.wrappers import doc_label_name

# parse the pseudo-xml document into a python-native dict
print "Downloading ap.tgz"
filename = wget.download('http://www.cs.princeton.edu/~blei/lda-c/ap.tgz')

print "parsing ap/ap.txt"
with tarfile.open(filename, 'r') as apfile:
    member = apfile.getmember('ap/ap.txt')
    ap89_f = apfile.extractfile(member)
    ap89_plain = ap89_f.read()

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

if not os.path.exists("ap"):
    os.mkdir("ap")

for doc,text in corpus.items():
    with open('ap/'+doc, 'w') as outfile:
        outfile.write(text)
