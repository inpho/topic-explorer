from argparse import ArgumentParser
import os
import os.path
import shutil
import platform
from StringIO import StringIO
import subprocess
import sys
import tarfile
import xml.etree.ElementTree as ET

import wget

from topicexplorer import init, prep, train

def download_and_extract():
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
        while remove is None or not (remove.startswith('y') or remove.startswith('n')):
            remove = raw_input("Remove? [Y/n] ")
            remove = remove.strip().lower()
            if remove == '' or remove.startswith('y'):
                shutil.rmtree("ap")
            elif remove.startswith('n'):
                sys.exit(74)

    # extracting to individual files
    os.mkdir("ap")
    print "Extracting documents to ap folder"
    for doc, text in corpus.items():
        with open('ap/' + doc, 'w') as outfile:
            outfile.write(text)


def main(args=None):
    download_and_extract()
        
    pwd = os.getcwd()

    init_parser = ArgumentParser()
    init.populate_parser(init_parser)
    args = init_parser.parse_args(
        ['ap', '--name', '"Associated Press 88-90 sample"', '--rebuild', '-q'])
    init.main(args)

    prep_parser = ArgumentParser()
    prep.populate_parser(prep_parser)
    args = prep_parser.parse_args('ap.ini --lang en --high 2000 --low 5 -q'.split())
    prep.main(args)

    train_parser = ArgumentParser()
    train.populate_parser(train_parser)
    args = train_parser.parse_args("ap.ini -k 20 40 60 --context-type article --iter 20".split())
    train.main(args)

    from ConfigParser import RawConfigParser as ConfigParser
    config = ConfigParser()
    config.read('ap.ini')
    config.set("main", "label_module", "topicexplorer.extensions.ap")
    config.set("www", "icons", "ap,link")
    with open("ap.ini", "wb") as configfh:
        config.write(configfh)


if __name__ == '__main__':
    main()
