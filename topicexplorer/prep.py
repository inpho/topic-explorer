from ConfigParser import RawConfigParser as ConfigParser
import json
import os.path

import nltk
import numpy as np
from scipy.stats import itemfreq

from vsm import *
from codecs import open 
from unidecode import unidecode
from topicexplorer.lib.util import isint, is_valid_filepath

# NLTK Langauges
langs = dict(da='danish', nl='dutch', en='english', fi='finnish', fr='french',
             de='german', hu='hungarian', it='italian', no='norwegian',
             pt='portuguese', ru='russian', es='spanish', sv='swedish',
             tr='turkish')

langs_rev = dict((v, k) for k, v in langs.items())

def stop_language(c, language):
    words = nltk.corpus.stopwords.words(language)
    words = [word for word in words if word in c.words]
    return c.apply_stoplist(words)

def main(args):
    config = ConfigParser({"htrc": False})
    config.read(args.config_file)
    args.corpus_path = config.get("main", "corpus_file")

    c = Corpus.load(args.corpus_path)
    
    if args.lang is None:
        args.lang = []
    
    # check for htrc metadata
    if args.htrc or config.get("main","htrc"):
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

    if args.lang is None:
        args.lang = []
    for lang in args.lang:
        print "Applying", langs[lang], "stopwords"
        c = stop_language(c, langs[lang])
    
    if args.stopword_file:
        print "Applying custom stopword file"
        with open(args.stopword_file, encoding='utf8') as swf:
            c = c.apply_stoplist([unidecode(word.strip()) for word in swf])
    
    
    print "\n\n*** FILTER HIGH FREQUENCY WORDS ***"
    items=itemfreq(c.corpus)
    counts = items[:,1]
    high_filter = False
    while not high_filter:
        bin_counts, bins = np.histogram(counts[counts.argsort()[::-1]], range=(0,len(c.words)/4.))
	print "{0:>10s} {1:>10s}".format("# Tokens", "# Words")
	for bin, count in zip(bins[1:], bin_counts):
	    print "{0:10.0f} {1:10.0f}".format(bin, count)
        print counts.sum(), "total tokens"
	print len(c.words), "total words"
    
        input_filter = 0
        accept = None
        while not input_filter:
            try:
                if high_filter:
                    input_filter = high_filter
                else:
                    input_filter = int(raw_input("Enter a top filter: "))
                candidates = c.words[items[:,0][counts > input_filter][counts[counts > input_filter].argsort()[::-1]]]
    
                print "Filter will remove", counts[counts > input_filter].sum(), "tokens", "of these", len(counts[counts > input_filter]), "words:"
                print ' '.join(candidates)

                print "\nFilter will remove", counts[counts > input_filter].sum(), "tokens", "of these", len(counts[counts > input_filter]), "words.",
    
                accept = None
                while accept not in ['y', 'n', 'c']:
                    accept = raw_input("\nAccept filter? [y/n/c/#] ")
                    if isint(accept):
                        high_filter = int(accept)
                        input_filter = 0
                        accept = 'n'
                    elif accept == 'y':
                        high_filter = input_filter
                    elif accept == 'c':
                        high_filter = -1
                        
            except ValueError:
                input_filter = 0 
    
    if high_filter > 0:
        print "Applying frequency filter > ", high_filter
        c = c.apply_stoplist(candidates)
    
    dirname = os.path.basename(args.corpus_path).split('-nltk-')[0]
    try:
        lowfreq = os.path.basename(args.corpus_path).split('-freq')[1].split('-')[0].split('.npz')[0]
    except:
        lowfreq = 5 

    def name_corpus(dirname, languages, lowfreq=5, highfreq=None):
        corpus_name = [dirname]
        if args.lang:
            corpus_name.append('nltk')
            corpus_name.append(''.join(args.lang))
        if lowfreq:
            corpus_name.append('freq%s'%lowfreq)
        if highfreq > 0:
            corpus_name.append('N%s'%highfreq)
        corpus_name = '-'.join(corpus_name)
        corpus_name += '.npz'
        return corpus_name
    
    corpus_name = name_corpus(dirname, ['en'], lowfreq, high_filter)
    model_path = os.path.dirname(args.corpus_path)
   
    args.corpus_path = os.path.join(model_path, corpus_name) 
    c.save(args.corpus_path)

    config.set("main", "corpus_file", args.corpus_path)
    with open(args.config_file, 'wb') as configfh:
        config.write(configfh)

def populate_parser(parser):
    parser.epilog = ('Available language stoplists (use 2-letter code): \n\t' + 
            '\n\t'.join(['{k}    {v}'.format(k=k, v=v.capitalize()) 
                          for k,v in sorted(langs.items(), 
                              key=lambda x: x[1])]))
    parser.add_argument("config_file", help="Path to Config",
        type=lambda x: is_valid_filepath(parser, x))
    parser.add_argument("--htrc", action="store_true")
    parser.add_argument("--stopword-file", dest="stopword_file",
        help="File with custom stopwords")
    parser.add_argument("--lang", nargs='+', choices=langs.keys(),
        help="Languages to stoplist. See options below.", metavar='xx')

if __name__ == '__main__':
    import argparse
    from argparse import ArgumentParser
    parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    populate_parser(parser)
    args = parser.parse_args()
    
    main(args)
