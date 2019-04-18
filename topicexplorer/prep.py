"""
Prepares a corpus for modeling with stoplist management tools.


Stoplisting
=============

What is stoplisting?
----------------------
Extremely common words can be of little value in discriminating between
documents and can create uninterpretable topics. Terms like ``the``, ``of``,
``is``, ``and``, ``but``, and ``or`` are thus excluded from modeling. These
terms are called *stop words*. The process of removing stop words is
stoplisting.


How ``topicexplorer prep`` generates stoplists
------------------------------------------------
``topicexplorer prep`` generates stoplists from the frequencies of words in the
collection being modeled, rather than using the same list of words across
different collections. Arbitrary lists can still be excluded with the 
|stopword-file argument|_.

.. |stopword-file argument| replace:: ``--stopword-file`` argument
.. _stopword-file argument: #custom-stopwords-stopword-file

While most natural language processing (NLP) tools exclude common words,
``topicexplorer prep`` also provides functionality to remove low-frequency
words. 

The contribution of low-freuqency words to the probability distribution
is negligible -- if a word only occurs once in a 1 million word corpus (which
can easily be hit with only 25-50 volumes), then it has a .000001 probability of
occurring. The runtime improvements gained from excluding these low frequency
words from the word-topic matrix far outweigh the marginal improvements to model
fit.

Another benefit of removing low-frequency words is the removal of spurious
tokens introduced by optical character recognition (OCR) in scanned documents.

Finally, very small words can be excluded with the |min-word-len argument|_.
These small words often appear when mathematical formulas are in a text (e.g.,
``y = mx + b`` would introduce ``y``, ``mx``, and ``b``). Usually, they will be
caught by the low-frequency filters, but this ensures they are left out.

.. |min-word-len argument| replace:: ``--min-word-len`` argument
.. _min-word-len argument: #small-words-min-word-len


.. seealso::
    `Introduction to Information Retrieval -- stop words`_
        Stanford textbook on stop words.

.. _Stop words:
.. _Introduction to Information Retrieval -- stop words:
    https://nlp.stanford.edu/IR-book/html/htmledition/dropping-common-terms-stop-words-1.html



Recommended Settings
======================
Each argument has a suggested value. A quick start, assuming your corpus is in
a folder called "workset" is::

    topicexplorer prep workset --high-percent 50 --low-percent 10 --min-word-len 3 -q

These parameters work well for English-language text. For languages without
articles (e.g., "a", "the"), we recommend reducing the ``--high-percent``
argument to ``--high-percent 25``.


Command Line Arguments
========================

High-probability words (``--high-percent``)
---------------------------------------------
Remove common words from the corpus, accounting for up to ``HIGH_PERCENT`` of
the total occurrences in the corpus.

**Recommended, but not default:** ``--high-percent 50``


Low-probability words (``--low-percent``)
-------------------------------------------
Remove uncommon words from the corpus, accounting for up to ``LOW_PERCENT`` of
the total occurrences in the corpus.

**Recommended, but not default:** ``--low-percent 10``


Small words (``--min-word-len``)
----------------------------------
Remove words with few characters from the corpus. Often includes mathematical
notation and OCR errors. 

**Recommended, but not default:** ``--min-word-len 3``


Custom stopwords (``-stopword-file``)
---------------------------------------
Remove custom words from the corpus.


Quiet mode (``-q``)
---------------------
Suppresses all user input requests. Uses default values unless otherwise
specified by other argument flags. Very useful for scripting automated
pipelines.

"""

from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import input
from builtins import zip
from builtins import str
from past.utils import old_div

import json
import os.path
import re
import sys

from codecs import open
from unidecode import unidecode

import topicexplorer.config
from topicexplorer.lib.util import isint, is_valid_configfile, bool_prompt

# NLTK Langauges
langs = dict(da='danish', nl='dutch', en='english', fi='finnish', fr='french',
             de='german', hu='hungarian', it='italian', no='norwegian',
             pt='portuguese', ru='russian', es='spanish', sv='swedish',
             tr='turkish')

langs_rev = dict((v, k) for k, v in langs.items())


def get_item_counts(x):
    from scipy.stats import itemfreq
    import numpy as np
    try:
        # for speed increase with numpy >= 1.9.0
        items, counts = np.unique(x, return_counts=True)
    except:
        # for compatability
        ifreq = itemfreq(x)
        items = ifreq[:, 0]
        counts = ifreq[:, 1]
    return items, counts

def get_corpus_counts(c):
    import numpy as np
    #print(len(c), len(c.words), len(c.context_data[0]))
    items = np.arange(len(c.words)) 
    counts = np.zeros(c.words.shape, dtype=np.int32)
    for context in c.view_contexts(c.context_types[0], as_slices=True):
        i, N = np.unique(c.corpus[context], return_counts=True)
        counts[i] += N

    return items, counts


def stop_language(c, language):
    import nltk.corpus

    try:
        words = nltk.corpus.stopwords.words(language)
    except LookupError:
        import sys
        print("\nERROR: stopwords not available, download by running:")
        print("    python -m nltk.downloader stopwords")
        print("\nExiting...")
        sys.exit(74)
    except IOError:
        print("{} unsupported by default, use a custom stopwords file.".format(language))
        return c.words

    if c.words.dtype.char == 'S':
        words = [word.strip() for word in words if word in c.words]
    else:
        words = [word for word in words if word in c.words]
    return words


def detect_langs(corpus):
    global langs
    import langdetect

    for doc in corpus.view_contexts(corpus.context_types[-1], as_strings=True):
        lang = langdetect.detect(' '.join(doc))
        return [lang]


def lang_prompt(languages):
    global langs
    out_langs = set()
    print("Stoplist the following languages?", end=' ')
    for lang in languages:
        if lang in langs:
            if bool_prompt("{}?".format(langs[lang].capitalize()), default=True):
                out_langs.add(lang)
    return out_langs


def get_candidate_words(c, n_filter, sort=True, words=None,
                        items=None, counts=None):
    """ Takes a corpus and a filter and reutrns the candidate words.
    If n_filter > 0, filter words occuring at least n_filter times.
    If n_filter < 0, filter words occuring less than n_filter times.
    """
    if n_filter == 0:
        return []
    else:
        if items is None or counts is None:
            items, counts = get_corpus_counts(c)

        if n_filter > 0:
            filter = items[counts >= n_filter]
            if sort:
                filter = filter[counts[counts >= n_filter].argsort()[::-1]]
    
        elif n_filter < 0:
            filter = items[counts <= -n_filter]
            if sort:
                filter = filter[counts[counts <= -n_filter].argsort()[::-1]]

        mask = get_mask(c, words, filter=filter)
        return c.words[mask]


def get_mask(c, words=None, filter=None):
    import numpy as np
    if filter is None:
        mask = np.ones(len(c.words), dtype=bool)  # all elements included/True.
    else:
        mask = np.zeros(len(c.words), dtype=bool)  # all elements excluded/False.
        mask[filter] = True

    if words is not None:
        ix = np.in1d(c.words, list(words))
        ix = np.where(ix)
        mask[ix] = False              # Set unwanted elements to False

    return mask[:]


def get_small_words(c, min_len):
    return [word for word in c.words if len(word) < min_len]


def get_closest_bin(c, thresh, reverse=False, counts=None):
    """
    Takes a corpus `c` and a `thresh`, returning the frequency that 
    is the lowest match for that threshold. Default is to count up, 
    selecting a lower bound threshold. If `reverse=True`, sums are
    reversed, selecting a filter for the higher bound.


    """
    import numpy as np
    
    # get counts
    if counts is None:
        _, counts = get_corpus_counts(c)

    if thresh == 0 and reverse:
        return max(counts) + 1
    elif thresh == 0 and not reverse:
        return 0
    else:
        # sort counts
        counts = counts[counts.argsort()]
        if reverse:
            counts = counts[::-1]

        # find insertion point
        cumsum = old_div(np.cumsum(counts), float(c.original_length))
        return counts[min(np.searchsorted(cumsum, thresh), len(counts)-1)]


def get_high_filter(c, words=None, items=None, counts=None):
    import numpy as np
    header = "FILTER HIGH FREQUENCY WORDS"
    stars = old_div((80 - len(header) - 2), 2)
    print("\n\n{0} {1} {0}".format('*' * stars, header))
    print("    This will remove all words occurring N or more times.")
    print("    The histogram below shows how many words will be removed")
    print("    by selecting each maximum frequency threshold.\n")

    # Get frequency bins
    if items is None or counts is None:
        items, counts = get_corpus_counts(c)
    bins = np.arange(1.0, -0.01, -0.025)
    bins = [get_closest_bin(c, thresh, counts=counts) for thresh in bins]
    bins = sorted(set(bins))
    bins.append(max(counts))

    high_filter = False
    while not high_filter:
        bin_counts, bins = np.histogram(counts, bins=bins)
        print("{0:>8s} {1:>8s} {2:<36s} {3:>14s} {4:>8s}".format("Rate", 'Top', '% of corpus',
                                                                 "# words", "Rate"))
        last_row = 0
        for bin, count in zip(bins[-2::-1], np.cumsum(bin_counts[::-1])):
            filtered_counts = counts[get_mask(c, words)]
            if (filtered_counts >= bin).sum() > last_row:
                percentage = 1. - (old_div(counts[counts < bin].sum(), float(c.original_length)))
                print("{0:>5.0f}x".format(bin).rjust(8), end=' ')
                print('{0:2.1f}%'.format(percentage * 100).rjust(8), end=' ')
                print((u'\u2588' * int(percentage * 36)).ljust(36), end=' ')
                print("  {0:0.0f} words".format((filtered_counts >= bin).sum()).rjust(14), end=' ')
                print(">= {0:>5.0f}x".format(bin).ljust(8))

            last_row = (filtered_counts >= bin).sum()

        print(' ' * 17, "{} total occurrences".format(counts.sum()).ljust(36), end=' ')
        print('{} words total'.format(get_mask(c, words).sum()).rjust(20))
        print('')

        input_filter = 0
        accept = None
        while not input_filter or input_filter <= 0:
            try:
                if high_filter:
                    input_filter = high_filter
                else:
                    input_filter = int(input("Enter the maximum rate: ").replace('x', ''))
                candidates = get_candidate_words(c, input_filter, words=words, items=items, counts=counts)
                places = np.in1d(c.words, candidates)
                places = dict(zip(candidates, np.where(places)[0]))
                candidates = sorted(candidates, key=lambda x: counts[places[x]], reverse=True)
                filtered_counts = counts[get_mask(c, words)]

                print("Filter will remove", filtered_counts[filtered_counts >= input_filter].sum(), end=' ')
                print("occurrences", "of these", len(filtered_counts[filtered_counts >= input_filter]), "words:")
                print(u' '.join(candidates))

                print("\nFilter will remove", filtered_counts[filtered_counts >= input_filter].sum(), end=' ')
                print("occurrences", "of these", len(filtered_counts[filtered_counts >= input_filter]), "words.", end=' ')
                if len(candidates) == len(c.words):
                    print("\n\nChoice of", input_filter, "will remove ALL words from the corpus.")
                    print("Please choose a different filter.")
                    high_filter = 0
                    input_filter = 0
                else:
                    accept = None
                    while accept not in ['y', 'n']:
                        accept = input("\nAccept filter? [y/n/[different max number]] ")
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


def get_low_filter(c, words=None, items=None, counts=None):
    import numpy as np
    header = "FILTER LOW FREQUENCY WORDS"
    stars = old_div((80 - len(header) - 2), 2)
    print("\n\n{0} {1} {0}".format('*' * stars, header))
    print("    This will remove all words occurring less than N times.")
    print("    The histogram below shows how many words will be removed")
    print("    by selecting each minimum frequency threshold.\n")

    # Get frequency bins
    if items is None or counts is None:
        items, counts = get_corpus_counts(c)
    bins = np.arange(1.0, -0.01, -0.025)
    bins = [get_closest_bin(c, thresh, reverse=True, counts=counts) for thresh in bins]
    bins = sorted(set(bins))
    bins.append(max(counts))

    low_filter = False
    while low_filter is False:
        bin_counts, bins = np.histogram(counts[counts.argsort()[::-1]], bins=bins)
        # print "{0:>10s} {1:>10s}".format("# Tokens", "# Words")
        print("{0:>8s} {1:>8s} {2:<36s} {3:>14s} {4:>8s}".format("Rate", 'Bottom', '% of corpus',
                                                                 "# words", "Rate"))

        last_row = 0
        for bin, count in zip(bins, np.cumsum(bin_counts)):
            filtered_counts = counts[get_mask(c, words)]
            if last_row < (filtered_counts < bin).sum() <= len(filtered_counts):
                percentage = (old_div(counts[counts <= bin].sum(), float(c.original_length)))
                print("{0:>5.0f}x".format(bin).rjust(8), end=' ')
                print('{0:2.1f}%'.format(percentage * 100).rjust(8), end=' ')
                print((u'\u2588' * int(percentage * 36)).ljust(36), end=' ')
                print("  {0:0.0f} words".format((filtered_counts <= bin).sum()).rjust(14), end=' ')
                print("<= {0:>5.0f}x".format(bin).ljust(8))
                if (filtered_counts < bin).sum() == len(filtered_counts):
                    break
            last_row = (filtered_counts >= bin).sum()


        print(' ' * 17, "{} total occurrences".format(counts.sum()).ljust(36), end=' ')
        print('{} words total'.format(get_mask(c, words).sum()).rjust(20))
        print('')

        input_filter = 0
        accept = None
        while not input_filter or input_filter <= 0:
            try:
                if low_filter:
                    input_filter = low_filter
                else:
                    input_filter = int(input("Enter the minimum rate: ").replace('x', ''))

                candidates = get_candidate_words(c, -input_filter, words=words, items=items, counts=counts)
                places = np.in1d(c.words, candidates)
                places = dict(zip(candidates, np.where(places)[0]))
                candidates = sorted(candidates, key=lambda x: counts[places[x]])
                filtered_counts = counts[get_mask(c, words)]

                print("Filter will remove", filtered_counts[filtered_counts <= input_filter].sum(), "tokens", end=' ')
                print("of these", len(filtered_counts[filtered_counts <= input_filter]), "words:")
                print(u' '.join(candidates))

                print("\nFilter will remove", filtered_counts[filtered_counts <= input_filter].sum(), "tokens", end=' ')
                print("of these", len(filtered_counts[filtered_counts <= input_filter]), "words.", end=' ')

                if len(candidates) == len(c.words):
                    print("\n\nChoice of", input_filter, "will remove ALL words from the corpus.")
                    print("Please choose a different filter.")
                    low_filter = 0
                    input_filter = 0
                else:
                    accept = None
                    while accept not in ['y', 'n']:
                        accept = input("\nAccept filter? [y/n/[different min. number] ")
                        if isint(accept):
                            low_filter = int(accept)
                            input_filter = 0
                            accept = 'n'
                        elif accept == 'y':
                            low_filter = input_filter
                        elif accept == 'n':
                            low_filter = False

            except ValueError:
                input_filter = 0

    return (low_filter, candidates)

def main(args):
    config = topicexplorer.config.read(args.config_file)

    if config.getboolean("main", "sentences"):
        from vsm.extensions.ldasentences import CorpusSent as Corpus
    else:
        from vsm.corpus import Corpus

    if args.lang is None:
        args.lang = []

    args.corpus_path = config.get("main", "corpus_file")
    c = Corpus.load(args.corpus_path)

    if c.original_length != len(c.corpus):
        print("Corpus has already been prepared. Proceed to training or")
        print("re-init the corpus to apply a different set of stopwords.")
        print("\nTIP: Train the LDA models with:")
        print("         topicexplorer train", args.config_file)
        sys.exit(1)

    # auto-guess a language
    """
    new_langs = [lang for lang in detect_langs(c) if lang in langs and lang not in args.lang]
    if new_langs:
        args.lang.extend(new_langs)
    """

    # add default locale if no other languages are specified
    # do not add if in quiet mode -- make everything explicit
    if not args.lang and not args.quiet:
        import locale
        locale = locale.getdefaultlocale()[0].split('_')[0].lower()
        if locale in langs.keys():
            args.lang.append(locale)

    # check for any new candidates
    args.lang = [lang for lang in args.lang if stop_language(c, langs[lang])]
    if args.lang and not args.quiet:
        args.lang = lang_prompt(args.lang)

    stoplist = set()
    # Apply stop words
    print(" ")
    for lang in args.lang:
        print("Applying", langs[lang], "stopwords")
        candidates = stop_language(c, langs[lang])
        if len(candidates):
            stoplist.update(candidates)

    # Apply custom stopwords file
    if args.stopword_file:
        with open(args.stopword_file, encoding='utf8') as swf:
            #candidates = [unidecode(word.strip()) for word in swf]
            candidates = [word.strip() for word in swf]

            if len(candidates):
                print("Applying custom stopword file to remove {} word{}.".format(
                    len(candidates), 's' if len(candidates) > 1 else ''))
                stoplist.update(candidates)
    
    if args.min_word_len:
        candidates = get_small_words(c, args.min_word_len)
        if len(candidates):
            print("Filtering {} small word{} with less than {} characters.".format(
                len(candidates), 's' if len(candidates) > 1 else '', args.min_word_len))
            stoplist.update(candidates)


    # cache item counts
    items, counts = get_corpus_counts(c)
    if args.high_filter is None and args.high_percent is None and not args.quiet:
        args.high_filter, candidates = get_high_filter(c, words=stoplist, items=items, counts=counts)
        if len(candidates):
            print("Filtering {} high frequency word{}.".format(len(candidates),
                                                               's' if len(candidates) > 1 else ''))
            stoplist.update(candidates)
    elif args.high_filter is None and args.high_percent is None and args.quiet:
        pass
    elif args.high_filter:
        candidates = get_candidate_words(c, args.high_filter, sort=False, items=items, counts=counts)
        if len(candidates):
            print("Filtering {} high frequency word{}.".format(len(candidates),
                                                               's' if len(candidates) > 1 else ''))
            stoplist.update(candidates)
    elif args.high_percent:
        args.high_filter = get_closest_bin(c, 1 - (args.high_percent / 100.), counts=counts)
        print(args.high_filter)
        candidates = get_candidate_words(c, args.high_filter, sort=False, items=items, counts=counts)
        if len(candidates):
            print("Filtering {} high frequency word{}.".format(len(candidates),
                                                               's' if len(candidates) > 1 else ''))
            stoplist.update(candidates)

    if args.low_filter is None and args.low_percent is None and not args.quiet:
        args.low_filter, candidates = get_low_filter(c, words=stoplist, items=items, counts=counts)
        if len(candidates):
            print("Filtering {} low frequency word{}.".format(len(candidates),
                                                              's' if len(candidates) > 1 else ''))
            stoplist.update(candidates)
    elif args.low_filter is None and args.low_percent is None and args.quiet:
        pass
    elif args.low_filter:
        candidates = get_candidate_words(c, -1 * args.low_filter, sort=False, items=items, counts=counts)
        if len(candidates):
            print("Filtering {} low frequency words.".format(len(candidates)))
            stoplist.update(candidates)

    elif args.low_percent:
        args.low_filter = get_closest_bin(c, 1 - (args.low_percent / 100.), reverse=True, counts=counts)
        print(args.low_filter)
        candidates = get_candidate_words(c, -1 * args.low_filter, sort=False, items=items, counts=counts)
        if len(candidates):
            print("Filtering {} low frequency word{}.".format(len(candidates),
                                                               's' if len(candidates) > 1 else ''))
            stoplist.update(candidates)



    if not stoplist:
        print("No stopwords applied.\n\n")

        sys.exit(0)
    else:
        print("\n\nApplying {} stopword{}".format(len(stoplist),
                                                  's' if len(stoplist) > 1 else ''))
        c.in_place_stoplist(stoplist)
        print("\n")

    def name_corpus(dirname, languages, lowfreq=None, highfreq=None):
        corpus_name = [dirname]

        if args.lang:
            corpus_name.append('nltk')
            corpus_name.append(''.join(args.lang))

        if lowfreq is not None and lowfreq > 0:
            corpus_name.append('freq%s' % lowfreq)
        if highfreq is not None and highfreq > 0:
            corpus_name.append('N%s' % highfreq)

        corpus_name = '-'.join(corpus_name)
        corpus_name += '.npz'
        return corpus_name

    dirname = os.path.basename(args.corpus_path).split('-nltk-')[0].replace('.npz', '')
    corpus_name = name_corpus(dirname, ['en'], args.low_filter, args.high_filter)

    model_path = os.path.dirname(args.corpus_path)
    args.corpus_path = os.path.join(model_path, corpus_name)
    c.save(args.corpus_path)

    config.set("main", "corpus_file", args.corpus_path)
    config.remove_option("main", "model_pattern")
    with open(args.config_file, 'w') as configfh:
        config.write(configfh)


def populate_parser(parser):
    import argparse
    parser.add_argument("config_file", help="Path to Config",
                        type=lambda x: is_valid_configfile(parser, x))

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--high", type=int, dest="high_filter",
                        help=argparse.SUPPRESS, default=None)
    group.add_argument("--high-percent", type=float, dest="high_percent",
                        help="High frequency word filter", default=None)
    
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--low", type=int, dest="low_filter",
                        default=None, help=argparse.SUPPRESS)
    group.add_argument("--low-percent", type=float, dest="low_percent",
                        default=None, help="Low frequency word filter")

    parser.add_argument("--min-word-len", type=int, dest="min_word_len",
                        default=0, help="Filter short words [Default: 0]")

    parser.add_argument("--stopword-file", dest="stopword_file",
                        help="File with custom stopwords")

    parser.add_argument("-q", "--quiet", help="Do not prompt for input",
                        action="store_true")

    parser.add_argument("--lang", nargs='+', choices=langs.keys(),
                        help=argparse.SUPPRESS, metavar='xx')
    """
    parser.epilog = ('Available language stoplists (use 2-letter code): \n\t' +
                     '\n\t'.join(['{k}    {v}'.format(k=k, v=v.capitalize())
                                  for k, v in sorted(langs.items(),
                                                     key=lambda x: x[1])]))
    """

if __name__ == '__main__':
    import argparse
    from argparse import ArgumentParser
    parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
