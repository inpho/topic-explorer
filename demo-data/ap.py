"""
Corpus preparation for VSM of the AP89 corpus.

Includes stoplisting based on nltk.corpus.stopwords.words('english') 
and frequency filtering <= 5.

This example can be used to help guide creation of other corpora for the 
Topic Explorer, in conjunction with the ap.ini file.
"""
import numpy as np
import os, os.path, shutil
from StringIO import StringIO
import tarfile
import xml.etree.ElementTree as ET
import sys


print "Checking for wget, unidecode and nltk packages"
def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', '--user', package])
    finally:
        globals()[package] = importlib.import_module(package)


install_and_import('wget')
install_and_import('unidecode')
install_and_import('nltk')

print "Checking for nltk stopwords and punkt tokenizer"
nltk.download('stopwords')
nltk.download('punkt')



from vsm import *
from vsm.extensions.corpusbuilders.util import apply_stoplist, word_tokenize
from vsm.viewer.wrappers import doc_label_name

# parse the pseudo-xml document into a python-native dict
if not os.path.exists('ap.tgz'):
    print "Downloading demo-data/ap.tgz"
    filename = wget.download('http://www.cs.princeton.edu/~blei/lda-c/ap.tgz')
else:
    print "Processing demo-data/ap.tgz"
    filename = 'ap.tgz'

print "\nParsing ap/ap.txt"
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

# check if directory already exists
if os.path.exists("ap"):
    print "Folder 'ap' already exists!"
    remove = None
    while remove is None or not (remove.startswith('y') or remove.startwith('n')):
        remove = raw_input("Remove? [Y/n] ")
        remove = remove.lower()
        if remove == '' or remove.startswith('y'):
            shutil.rmtree("ap")
        elif remove.startswith('n'):
            sys.exit(74)

# extracting to individual files
os.mkdir("ap")
print "Extracting documents to demo-data/ap folder"
for doc,text in corpus.items():
    with open('ap/'+doc, 'w') as outfile:
        outfile.write(text)

