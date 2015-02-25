from argparse import ArgumentParser
from ConfigParser import RawConfigParser as ConfigParser
import json
import os.path

import nltk
import numpy as np
from scipy.stats import itemfreq

from vsm import *

parser = ArgumentParser()
parser.add_argument("corpus_path", help="Path to Existing Corpus File")
parser.add_argument("--htrc", action="store_true")
parser.add_argument("--lang", nargs='+', help="Languages to stoplist")
args = parser.parse_args()

c = Corpus.load(args.corpus_path)

# NLTK Langauges
langs = dict(da='danish', nl='dutch', en='english', fi='finnish', fr='french',
             de='german', hu='hungarian', it='italian', no='norwegian',
             pt='portuguese', ru='russian', es='spanish', sv='swedish',
             tr='turkish')

langs_rev = dict((v, k) for k, v in langs.items())

if args.lang is None:
    args.lang = []

# check for htrc metadata
if args.htrc:
    metadata_path = os.path.dirname(args.corpus_path)
    metadata_path = os.path.join(metadata_path, '../metadata.json')
    if os.path.exists(metadata_path):
        print "HTRC metadata file found!"
        with open(metadata_path) as jsonfile:
            data = json.load(jsonfile)

        md_langs = set([lang for d in data.values() for lang in d.get('language', list())
            if lang.lower() in langs.values()])
        
        print "Stoplist the following languages?"
        for lang in md_langs:
            accept = None
            while accept not in ['y','n']:
                accept = raw_input(lang + "? [y/n] ") 
            if accept == 'y':
                code = langs_rev[lang.lower()]
                if code not in args.lang:
                    args.lang.append(code)

def stop_language(c, language):
    words = nltk.corpus.stopwords.words(language)
    words = [word for word in words if word in c.words]
    return c.apply_stoplist(words)
if args.lang is None:
    args.lang = []
for lang in args.lang:
    print "Applying", langs[lang], "stopwords"
    c = stop_language(c, langs[lang])


print "\n\n*** FILTER HIGH FREQUENCY WORDS ***"
items=itemfreq(c.corpus)
counts = items[:,1]
high_filter = False
while not high_filter:
    bin_counts, bins = np.histogram(items[:,1][items[:,1].argsort()[::-1]], range=(0,len(c.words)/4.))
    print "Freq   ",
    for bin in bins:
        print "%10.0f" % bin,
    print "\nWords   ",
    for count in bin_counts:
        print "%10.0f" % count,
    print "\n"
    print counts.sum(), "total words"

    input_filter = 0
    while not input_filter:
        try:
            input_filter = int(raw_input("Enter a top filter: "))
            candidates = c.words[items[:,0][counts > input_filter][counts[counts > input_filter].argsort()[::-1]]]

            print counts[counts > input_filter].sum(), "Words"
            print ' '.join(candidates)
            print counts[counts > input_filter].sum(), "Words"

            accept = None
            while accept not in ['y', 'n', 'c']:
                accept = raw_input("\nAccept filter? [y/n/c] ")
                if accept == 'y':
                    high_filter = input_filter
                if accept == 'c':
                    high_filter = -1
        except ValueError:
            input_filter = 0 

if high_filter > 0:
    print "Applying frequency filter > ", high_filter
    c = c.apply_stoplist(candidates)

dirname = os.path.basename(args.corpus_path).split('-nltk-')[0]
lowfreq = os.path.basename(args.corpus_path).split('-freq')[1].split('-')[0].split('.npz')[0]
def name_corpus(dirname, languages, lowfreq=5, highfreq=None):
    corpus_name = dirname
    corpus_name += '-nltk-' + ''.join(args.lang)
    corpus_name += '-' + 'freq%s'%lowfreq
    if highfreq > 0:
        corpus_name += '-N%s'%highfreq
    corpus_name += '.npz'
    return corpus_name

corpus_name = name_corpus(dirname, ['en'], lowfreq, high_filter)
model_path = os.path.dirname(args.corpus_path)

c.save(os.path.join(model_path, corpus_name))
