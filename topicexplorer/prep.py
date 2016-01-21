from ConfigParser import RawConfigParser as ConfigParser
import json
import os.path
import re

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

def get_items_counts(x):
    try:
        # for speed increase with numpy >= 1.9.0
        items, counts = np.unique(x, return_counts=True)
    except:
        # for compatability
        ifreq = itemfreq(x)
        items = ifreq[:,0]
        counts = ifreq[:,1]
    return items, counts



def stop_language(c, language):
    words = nltk.corpus.stopwords.words(language)
    if c.words.dtype.char == 'S':
        words = [unidecode(word.strip()) for word in words if word in c.words]
    else:
        words = [word for word in words if word in c.words]
    return words

def get_htrc_langs(args):
    global langs
    out_langs = []

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
                    out_langs.append(code)

def get_candidate_words(c, n_filter, sort=True):
    """ Takes a corpus and a filter and reutrns the candidate words. 
    If n_filter > 0, filter words occuring at least n_filter times.
    If n_filter < 0, filter words occuring less than n_filter times.
    """
    items, counts = get_items_counts(c.corpus)
    if n_filter > 0:
        filter = items[counts > n_filter]
        if sort:
            filter = filter[counts[counts > n_filter].argsort()[::-1]]

    elif n_filter < 0:
        filter = items[counts < -n_filter]
        if sort:
            filter = filter[counts[counts < -n_filter].argsort()[::-1]]

    return c.words[filter]

def get_small_words(c, min_len):
    return [word for word in c.words if len(word) < min_len]

def get_special_chars(c):
    return [word for word in c.words if re.findall('[^A-Za-z\-\']', word)]


def get_high_filter(args, c):
    print "\n\n*** FILTER HIGH FREQUENCY WORDS ***"
    items, counts = get_items_counts(c.corpus)
    high_filter = False
    while not high_filter:
        bin_counts, bins = np.histogram(counts[counts.argsort()[::-1]], range=(0,len(c.words)/4.))
	#print "{0:>10s} {1:>10s}".format("# Tokens", "# Words")
	for bin, count in zip(bins[1:], bin_counts):
	    print "{1:0.0f} words occur more than {0:0.0f} times".format(bin, count)
        print counts.sum(), "total occurrences"
	print len(c.words), "total words"
    
        input_filter = 0
        accept = None
        while not input_filter:
            try:
                if high_filter:
                    input_filter = high_filter
                else:
                    input_filter = int(raw_input("Enter the maximum word occurence rate: "))
                candidates = get_candidate_words(c, input_filter)
    
                print "Filter will remove", counts[counts > input_filter].sum(), "occurrences", "of these", len(counts[counts > input_filter]), "words:"
                print ' '.join(candidates)

                print "\nFilter will remove", counts[counts > input_filter].sum(), "occurrences", "of these", len(counts[counts > input_filter]), "words.",
                if len(candidates) == len(c.words):
                    print "\n\nChoice of",input_filter, "will remove ALL words from the corpus."
                    print "Please choose a different filter."
                    high_filter = 0
                    input_filter = 0
                else:
                    accept = None
                    while accept not in ['y', 'n']:
                        accept = raw_input("\nAccept filter? [y/n/[different max number]] ")
                        if isint(accept):
                            high_filter = int(accept)
                            input_filter = 0
                            accept = 'n'
                        elif accept == 'y':
                            high_filter = input_filter
                        elif accept == 'n':
                            high_filter = 0
                        
            except ValueError:
                input_filter = 0 

    return (high_filter, candidates)

def get_low_filter(args, c):
    print "\n\n*** FILTER LOW FREQUENCY WORDS ***"
    items, counts = get_items_counts(c.corpus)

    low_filter = False
    while not low_filter:
        bin_counts, bins = np.histogram(counts[counts.argsort()[::-1]], range=(0,len(c.words)/20.))
	#print "{0:>10s} {1:>10s}".format("# Tokens", "# Words")
	for bin, count in zip(bins[:-1], bin_counts):
	    print "{1:10.0f} words occur less than {0:10.0f} times".format(bin, count)
        print counts.sum(), "total occurrences"
	print len(c.words), "total words"
    
        input_filter = 0
        accept = None
        while not input_filter:
            try:
                if low_filter:
                    input_filter = low_filter
                else:
                    input_filter = int(raw_input("Enter the minimum word occurrence rate: "))
                candidates = get_candidate_words(c, -input_filter)
    
                print "Filter will remove", counts[counts < input_filter].sum(), "tokens", "of these", len(counts[counts < input_filter]), "words:"
                print ' '.join(candidates)

                print "\nFilter will remove", counts[counts < input_filter].sum(), "tokens", "of these", len(counts[counts < input_filter]), "words.",
                
                if len(candidates) == len(c.words):
                    print "\n\nChoice of",input_filter, "will remove ALL words from the corpus."
                    print "Please choose a different filter."
                    low_filter = 0
                    input_filter = 0
                else:
                    accept = None
                    while accept not in ['y', 'n']:
                        accept = raw_input("\nAccept filter? [y/n/[different min. number] ")
                        if isint(accept):
                            low_filter = int(accept)
                            input_filter = 0
                            accept = 'n'
                        elif accept == 'y':
                            low_filter = input_filter
                        elif accept == 'n':
                            low_filter = 0
                        
            except ValueError:
                input_filter = 0 

    return (low_filter, candidates)

def main(args):
    config = ConfigParser({"htrc": False})
    config.read(args.config_file)
    
    if args.lang is None:
        args.lang = []

    
    
    args.corpus_path = config.get("main", "corpus_file")
    c = Corpus.load(args.corpus_path)
    
    # check for htrc metadata
    if args.htrc or config.get("main","htrc"):
        htrc_langs = get_htrc_langs(args)
        if htrc_langs:
            args.lang.extend(htrc_langs)

    stoplist = set() 
    # Apply stop words
    for lang in args.lang:
        print "Applying", langs[lang], "stopwords"
        candidates = stop_language(c, langs[lang])
        if len(candidates):
            stoplist.update(candidates)
        print len(candidates), len(stoplist) 

    # Apply custom stopwords file
    if args.stopword_file:
        print "Applying custom stopword file"
        with open(args.stopword_file, encoding='utf8') as swf:
            candidates = [unidecode(word.strip()) for word in swf]
            if len(candidates):
                stoplist.update(candidates)
        print len(candidates), len(stoplist) 

    if args.min_word_len:
        print "filtering small words"
        candidates = get_small_words(c, args.min_word_len)
        if len(candidates):
            stoplist.update(candidates)
        print len(candidates), len(stoplist) 
    
    if not args.special_chars:
        print "filtering words with special chars"
        candidates = get_special_chars(c)
        if len(candidates):
            stoplist.update(candidates)
        print len(candidates), len(stoplist)
   
    print "adding high frequency filter" 
    if not args.high_filter:
        high_filter, candidates = get_high_filter(args, c)
        if len(candidates):
            stoplist.update(candidates)
    else:
        high_filter = args.high_filter
        candidates = get_candidate_words(c,args.high_filter, sort=False)
        if len(candidates):
            stoplist.update(candidates)
    print len(candidates), len(stoplist) 

    print "adding low frequency filter" 
    if not args.low_filter:
        low_filter, candidates = get_low_filter(args, c)
        if len(candidates):
            stoplist.update(candidates)
    else:
        low_filter = args.low_filter
        candidates  = get_candidate_words(c, -1*args.low_filter, sort=False)
        if len(candidates):
            stoplist.update(candidates)
    print len(candidates), len(stoplist) 

    if stoplist:
        print "applying {} stopwords".format(len(stoplist))
        c.in_place_stoplist(stoplist)

    def name_corpus(dirname, languages, lowfreq=None, highfreq=None):
        items, counts = get_items_counts(c.corpus)

        corpus_name = [dirname]
        if args.lang:
            corpus_name.append('nltk')
            corpus_name.append(''.join(args.lang))
        if lowfreq > 0:
            corpus_name.append('freq%s'%lowfreq)
        else:
            corpus_name.append('freq%s'%min(counts))

        if highfreq > 0:
            corpus_name.append('N%s'%highfreq)
        else:
            corpus_name.append('freq%s'%max(counts))

        corpus_name = '-'.join(corpus_name)
        corpus_name += '.npz'
        return corpus_name
   
    dirname = os.path.basename(args.corpus_path).split('-nltk-')[0].replace('.npz','')
    corpus_name = name_corpus(dirname, ['en'], low_filter, high_filter)

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
    parser.add_argument("--high", type=int, dest="high_filter",
        help="High frequency word filter", default=None)
    parser.add_argument("--low", type=int, dest="low_filter",
        default=5, help="Low frequency word filter [Default: 5]")
    parser.add_argument("--min-word-len", type=int, dest="min_word_len",
        default=3, help="Low frequency word filter [Default: 3]")
    parser.add_argument("--exclude-special-chars", action="store_false",
        dest='special_chars')
    parser.add_argument("--lang", nargs='+', choices=langs.keys(),
        help="Languages to stoplist. See options below.", metavar='xx')

if __name__ == '__main__':
    import argparse
    from argparse import ArgumentParser
    parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    populate_parser(parser)
    args = parser.parse_args()
    
    main(args)
