from ConfigParser import RawConfigParser as ConfigParser
import json
import os.path
import re
import sys

from codecs import open
from unidecode import unidecode
from topicexplorer.lib.util import isint, is_valid_configfile, bool_prompt

# NLTK Langauges
langs = dict(da='danish', nl='dutch', en='english', fi='finnish', fr='french',
             de='german', hu='hungarian', it='italian', no='norwegian',
             pt='portuguese', ru='russian', es='spanish', sv='swedish',
             tr='turkish')

langs_rev = dict((v, k) for k, v in langs.items())


def get_items_counts(x):
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


def stop_language(c, language):
    import nltk.corpus

    try:
        words = nltk.corpus.stopwords.words(language)
    except LookupError:
        import sys
        print "\nERROR: stopwords not available, download by running:"
        print "    python -m nltk.downloader stopwords"
        print "\nExiting..."
        sys.exit(74)
    except IOError:
        print "{} unsupported by default, use a custom stopwords file."
        return c.words

    if c.words.dtype.char == 'S':
        words = [word.strip() for word in words if word in c.words]
    else:
        words = [word for word in words if word in c.words]
    return words


def get_htrc_langs(args):
    global langs
    md_langs = []

    metadata_path = os.path.dirname(args.corpus_path)
    metadata_path = os.path.join(metadata_path, '../metadata.json')
    if os.path.exists(metadata_path):
        print "HTRC metadata file found!"
        with open(metadata_path) as jsonfile:
            data = json.load(jsonfile)

        md_langs = set([lang for d in data.values() for lang in d.get('language', list())
            if lang.lower() in langs.values()])
    
    return md_langs


def detect_langs(corpus):
    global langs
    import langdetect

    for doc in corpus.view_contexts(corpus.context_types[-1], as_strings=True):
        lang = langdetect.detect(' '.join(doc))
        return [lang]


def lang_prompt(languages):
    global langs
    out_langs = set()
    print "Stoplist the following languages?",
    for lang in languages:
        if lang in langs:
            if bool_prompt("{}?".format(langs[lang].capitalize()), default=True):
                out_langs.add(lang)
    return out_langs


def get_candidate_words(c, n_filter, sort=True, words=None):
    """ Takes a corpus and a filter and reutrns the candidate words.
    If n_filter > 0, filter words occuring at least n_filter times.
    If n_filter < 0, filter words occuring less than n_filter times.
    """
    items, counts = get_items_counts(c.corpus)
    if n_filter >= 0:
        filter = items[counts > n_filter]
        if sort:
            filter = filter[counts[counts > n_filter].argsort()[::-1]]

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

    if words:
        ix = np.in1d(c.words, list(words))
        ix = np.where(ix)
        mask[ix] = False              # Set unwanted elements to False

    return mask[:]


def get_small_words(c, min_len):
    return [word for word in c.words if len(word) < min_len]


def get_special_chars(c):
    return [word for word in c.words if re.findall('[^A-Za-z\-\']', word)]


def get_high_filter(args, c, words=None):
    import numpy as np
    header = "FILTER HIGH FREQUENCY WORDS"
    stars = (80 - len(header) - 2) / 2
    print "\n\n{0} {1} {0}".format('*' * stars, header)
    print "    This will remove all words occurring more than N times."
    print "    The histogram below shows how many words will be removed"
    print "    by selecting each maximum frequency threshold.\n"
    items, counts = get_items_counts(c.corpus)
    items = items[get_mask(c, words)]
    counts = counts[get_mask(c, words)]
    high_filter = False
    bins = np.array([0., 0.025, 0.05, 0.075, 0.1, 0.15, 0.20, 0.25, 0.3, 0.35, 0.4, 0.5, 1.0])
    bins = 1. - bins

    thresh = np.cumsum(counts[counts.argsort()]) / float(counts.sum())
    bins = [counts[counts.argsort()][np.searchsorted(thresh, bin)] for bin in bins]
    bins = sorted(set(bins))
    bins.append(max(counts))

    while not high_filter:
        bin_counts, bins = np.histogram(counts, bins=bins)
        print "{0:>8s} {1:>8s} {2:<36s} {3:>14s} {4:>8s}".format("Rate", 'Top', '% of corpus',
                                                                 "# words", "Rate")
        for bin, count in zip(bins[-2::-1], np.cumsum(bin_counts[::-1])):
            if count:
                percentage = 1. - (counts[counts < bin].sum() / float(counts.sum()))
                print "{0:>5.0f}x".format(bin - 1).rjust(8),
                print '{0:2.1f}%'.format(percentage * 100).rjust(8),
                print (u'\u2588' * (percentage * 36)).ljust(36),
                print "  {0:0.0f} words".format(count).rjust(14),
                print "> {0:>5.0f}x".format(bin - 1).ljust(8)

        print ' ' * 17, "{} total occurrences".format(counts.sum()).ljust(36),
        print '{} words total'.format(get_mask(c, words).sum()).rjust(20)
        print ''

        input_filter = 0
        accept = None
        while not input_filter or input_filter <= 0:
            try:
                if high_filter:
                    input_filter = high_filter
                else:
                    input_filter = int(raw_input("Enter the maximum rate: ").replace('x', ''))
                candidates = get_candidate_words(c, input_filter, words=words)
                places = np.in1d(c.words[get_mask(c, words)], candidates)
                places = dict(zip(candidates, np.where(places)[0]))
                candidates = sorted(candidates, key=lambda x: counts[places[x]], reverse=True)

                print "Filter will remove", counts[counts > input_filter].sum(),
                print "occurrences", "of these", len(counts[counts > input_filter]), "words:"
                print u' '.join(candidates).encode(
                    sys.stdout.encoding, errors='replace')

                print "\nFilter will remove", counts[counts > input_filter].sum(),
                print "occurrences", "of these", len(counts[counts > input_filter]), "words.",
                if len(candidates) == len(c.words):
                    print "\n\nChoice of", input_filter, "will remove ALL words from the corpus."
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


def get_low_filter(args, c, words=None):
    import numpy as np
    header = "FILTER LOW FREQUENCY WORDS"
    stars = (80 - len(header) - 2) / 2
    print "\n\n{0} {1} {0}".format('*' * stars, header)
    print "    This will remove all words occurring less than N times."
    print "    The histogram below shows how many words will be removed"
    print "    by selecting each minimum frequency threshold.\n"
    items, counts = get_items_counts(c.corpus)
    items = items[get_mask(c, words)]
    counts = counts[get_mask(c, words)]

    bins = np.linspace(0, 1.0, 11)
    bins = 1. - np.array([0., 0.025, 0.05, 0.075, 0.1, 0.15, 0.20, 0.25, 0.3, 0.35, 0.4, 0.5, 1.0])

    thresh = np.cumsum(counts[counts.argsort()[::-1]]) / float(counts.sum())
    bins = [counts[counts.argsort()[::-1]][np.searchsorted(thresh, bin)] for bin in bins]
    bins = sorted(set(bins))

    low_filter = False
    while low_filter is False:
        bin_counts, bins = np.histogram(counts[counts.argsort()[::-1]], bins=bins)
        # print "{0:>10s} {1:>10s}".format("# Tokens", "# Words")
        print "{0:>8s} {1:>8s} {2:<36s} {3:>14s} {4:>8s}".format("Rate", 'Bottom', '% of corpus',
                                                                 "# words", "Rate")
        for bin, count in zip(bins[1:], np.cumsum(bin_counts)):
            if count:
                percentage = (counts[counts <= bin].sum() / float(counts.sum()))
                print "{0:>5.0f}x".format(bin - 1).rjust(8),
                print '{0:2.1f}%'.format(percentage * 100).rjust(8),
                print (u'\u2588' * (percentage * 36)).ljust(36),
                print "  {0:0.0f} words".format(count).rjust(14),
                print "<= {0:>5.0f}x".format(bin - 1).ljust(8)

        print ' ' * 17, "{} total occurrences".format(counts.sum()).ljust(36),
        print '{} words total'.format(get_mask(c, words).sum()).rjust(20)
        print ''

        input_filter = 0
        accept = None
        while not input_filter or input_filter <= 0:
            try:
                if low_filter:
                    input_filter = low_filter
                else:
                    input_filter = int(raw_input("Enter the minimum rate: ").replace('x', ''))

                candidates = get_candidate_words(c, -input_filter, words=words)
                places = np.in1d(c.words[get_mask(c, words)], candidates)
                places = dict(zip(candidates, np.where(places)[0]))
                candidates = sorted(candidates, key=lambda x: counts[places[x]])

                print "Filter will remove", counts[counts <= input_filter].sum(), "tokens",
                print "of these", len(counts[counts <= input_filter]), "words:"
                print u' '.join(candidates).encode(
                    sys.stdout.encoding, errors='replace')

                print "\nFilter will remove", counts[counts <= input_filter].sum(), "tokens",
                print "of these", len(counts[counts <= input_filter]), "words.",

                if len(candidates) == len(c.words):
                    print "\n\nChoice of", input_filter, "will remove ALL words from the corpus."
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
                            low_filter = False

            except ValueError:
                input_filter = 0

    return (low_filter, candidates)


def main(args):
    config = ConfigParser({"htrc": False,
                           "sentences": "False"})
    config.read(args.config_file)

    if config.getboolean("main", "sentences"):
        from vsm.extensions.ldasentences import CorpusSent as Corpus
    else:
        from vsm.corpus import Corpus

    if args.lang is None:
        args.lang = []

    args.corpus_path = config.get("main", "corpus_file")
    c = Corpus.load(args.corpus_path)

    # check for htrc metadata
    if args.htrc or config.get("main", "htrc"):
        htrc_langs = get_htrc_langs(args)
        if htrc_langs:
            args.lang.extend(new_langs)

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
    print " "
    for lang in args.lang:
        print "Applying", langs[lang], "stopwords"
        candidates = stop_language(c, langs[lang])
        if len(candidates):
            stoplist.update(candidates)

    # Apply custom stopwords file
    if args.stopword_file:
        with open(args.stopword_file, encoding='utf8') as swf:
            #candidates = [unidecode(word.strip()) for word in swf]
            candidates = [word.strip() for word in swf]

            if len(candidates):
                print "Applying custom stopword file to remove {} word{}.".format(
                    len(candidates), 's' if len(candidates) > 1 else '')
                stoplist.update(candidates)

    if args.min_word_len:
        candidates = get_small_words(c, args.min_word_len)
        if len(candidates):
            print "Filtering {} small word{} with less than {} characters.".format(
                len(candidates), 's' if len(candidates) > 1 else '', args.min_word_len)
            stoplist.update(candidates)

    if not args.special_chars:
        candidates = get_special_chars(c)
        if len(candidates):
            print "Filtering {} word{} with special characters.".format(
                len(candidates), 's' if len(candidates) > 1 else '')
            stoplist.update(candidates)

    if args.high_filter is None and not args.quiet:
        args.high_filter, candidates = get_high_filter(args, c, words=stoplist)
        if len(candidates):
            print "Filtering {} high frequency word{}.".format(len(candidates),
                                                               's' if len(candidates) > 1 else '')
            stoplist.update(candidates)
    elif args.high_filter > 0:
        candidates = get_candidate_words(c, args.high_filter, sort=False)
        if len(candidates):
            print "Filtering {} high frequency word{}.".format(len(candidates),
                                                               's' if len(candidates) > 1 else '')
            stoplist.update(candidates)

    if args.low_filter is None and not args.quiet:
        args.low_filter, candidates = get_low_filter(args, c, words=stoplist)
        if len(candidates):
            print "Filtering {} low frequency word{}.".format(len(candidates),
                                                              's' if len(candidates) > 1 else '')
            stoplist.update(candidates)
    elif args.low_filter > 0:
        candidates = get_candidate_words(c, -1 * args.low_filter, sort=False)
        if len(candidates):
            print "Filtering {} low frequency words.".format(len(candidates))
            stoplist.update(candidates)

    if not stoplist:
        print "No stopwords applied.\n\n"

        sys.exit(0)
    else:
        print "\n\nApplying {} stopword{}".format(len(stoplist),
                                                  's' if len(stoplist) > 1 else '')
        c.in_place_stoplist(stoplist)
        print "\n"

    def name_corpus(dirname, languages, lowfreq=None, highfreq=None):
        items, counts = get_items_counts(c.corpus)

        corpus_name = [dirname]
        if args.lang:
            corpus_name.append('nltk')
            corpus_name.append(''.join(args.lang))
        if lowfreq > 0:
            corpus_name.append('freq%s' % lowfreq)
        else:
            corpus_name.append('freq%s' % min(counts))

        if highfreq > 0:
            corpus_name.append('N%s' % highfreq)
        else:
            corpus_name.append('freq%s' % max(counts))

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
    with open(args.config_file, 'wb') as configfh:
        config.write(configfh)


def populate_parser(parser):
    parser.epilog = ('Available language stoplists (use 2-letter code): \n\t' +
                     '\n\t'.join(['{k}    {v}'.format(k=k, v=v.capitalize())
                                  for k, v in sorted(langs.items(),
                                                     key=lambda x: x[1])]))
    parser.add_argument("config_file", help="Path to Config",
                        type=lambda x: is_valid_configfile(parser, x))
    parser.add_argument("--htrc", action="store_true")
    parser.add_argument("--stopword-file", dest="stopword_file",
                        help="File with custom stopwords")
    parser.add_argument("--high", type=int, dest="high_filter",
                        help="High frequency word filter", default=None)
    parser.add_argument("--low", type=int, dest="low_filter",
                        default=None, help="Low frequency word filter")
    parser.add_argument("--min-word-len", type=int, dest="min_word_len",
                        default=0, help="Filter short words [Default: 0]")
    parser.add_argument("--exclude-special-chars", action="store_false",
                        dest='special_chars')
    parser.add_argument("--lang", nargs='+', choices=langs.keys(),
                        help="Languages to stoplist. See options below.", metavar='xx')
    parser.add_argument("-q", "--quiet", help="Do not prompt for input",
                        action="store_true")

if __name__ == '__main__':
    import argparse
    from argparse import ArgumentParser
    parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
