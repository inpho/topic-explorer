from argparse import ArgumentParser
import numpy as np

from vsm.corpus import *

parser = ArgumentParser()
parser.add_argument("corpus_path", help="Path to Existing Corpus File")
args = parser.parse_args()

c = Corpus.load(args.corpus_path)
pagenos = [int(md['file'].split('/')[-1].replace('.txt',''))
    for md in c.view_metadata('page')]
pagenos = np.array(pagenos)

c = add_metadata(c, 'page', 'seq_number', pagenos)
c.save(args.corpus_path)
