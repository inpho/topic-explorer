"""
Program to build a Corpus object, train LDA models and finally build a config
file for the topic explorer.
"""
import multiprocessing
import os
import os.path
import sys

from vsm.corpus import Corpus
from vsm.corpus.util.corpusbuilders import coll_corpus, dir_corpus, toy_corpus
from vsm.model.lda import LDA
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer

def build_models(corpus_filename, model_path, krange, n_iterations=200,
                 n_proc=2, seed=None, corpus_type=None):

    corpus = Corpus.load(corpus_filename)
    if corpus_type is None:
        corpus_type = 'book' if 'book' in corpus.context_types else 'document'

    basefilename = os.path.basename(corpus_filename).replace('.npz','')
    basefilename += "-LDA-K%s-%s-%d.npz" % ('{0}', corpus_type, n_iterations)
    basefilename = os.path.join(model_path, basefilename)

    if type(seed) == int:
        seeds = [seed + p for p in range(n_proc)]
        fileparts = basefilename.split('-')
        fileparts.insert(-1, str(seed))
        basefilename = '-'.join(fileparts)
    else:
        seeds = None

    for k in krange:
        print "Training model for k={0} Topics with {1} Processes"\
            .format(k, n_proc)
        m = LDA(corpus, corpus_type, K=k, multiprocessing=True)
        m.train(n_iterations=n_iterations, n_proc=n_proc, seeds=seeds)
        m.save(basefilename.format(k))

    return basefilename

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ConfigParser import RawConfigParser as ConfigParser
    parser = ArgumentParser()
    parser.add_argument("corpus_filename", help="Path to Corpus file")
    parser.add_argument("--model-path", dest="model_path",
        help="Model Path [Default: [corpus_path]/../models]")
    parser.add_argument("--htrc", action="store_true")
    parser.add_argument("--corpus-type", dest="corpus_type")
    parser.add_argument("-p", "--processes", default=2, type=int,
        help="Number of CPU cores for training [Default: 2]")
    parser.add_argument("--port", default=16000, type=int,
        help="Default port [Default: 16000]")
    parser.add_argument("--seed", default=None, type=int,
        help="Random seed for topic modeling [Default: None]")
    parser.add_argument("-k", nargs='+',
        help="K values to train upon", type=int)
    parser.add_argument("--retrain", action="store_true")
    parser.add_argument('--iter', type=int,
        help="Number of training iterations")
    parser.add_argument('--dry-run', action="store_true",
        help="Only create corpus object and config file, not models")
    args = parser.parse_args()
   
    if not os.path.exists(args.corpus_filename):
        print "ERROR: Invalid Corpus file."
        sys.exit(74)

    if args.model_path is None:
        args.model_path = os.path.dirname(args.corpus_filename)
    if not os.path.exists(args.model_path):
        os.makedirs(args.model_path)

    if args.corpus_type is None:
        # TODO: Prompt for corpus type selection
        pass

    if args.k is None:
        args.k = range(120,0,-20)
    
    if args.iter is None and not args.dry_run:
        while args.iter is None:
            iters = raw_input("Number of Training Iterations [Default 200]: ")
            try:
                args.iter = int(iters)
            except ValueError:
                if iters.strip() == '':
                    args.iter = 200
                else:
                    print "Enter a valid integer!"

        print "\nTIP: number of training iterations can be specified with argument '--iter N':"
        print "python retrain.py --iter %d %s\n" % (args.iter, args.corpus_filename)

    if args.processes < 0:
        args.processes = multiprocessing.cpu_count() + args.processes

    if args.dry_run:
        model_pattern = build_models(args.corpus_filename, args.model_path, list(),
                                     n_iterations=args.iter,
                                     n_proc=args.processes, seed=args.seed,
                                     corpus_type=args.corpus_type)
    else:
        model_pattern = build_models(args.corpus_filename, args.model_path, args.k,
                                     n_iterations=args.iter,
                                     n_proc=args.processes, seed=args.seed,
                                     corpus_type=args.corpus_type)

    corpus = Corpus.load(args.corpus_filename)

    corpus_name = os.path.basename(args.corpus_filename).split('-')[0]

    config = ConfigParser()
    config.add_section("main")
    config.set("main", "path", args.model_path)
    config.set("main", "corpus_file", args.corpus_filename)
    config.set("main", "context_type", args.corpus_type)
    config.set("main", "model_pattern", model_pattern)
    config.set("main", "port", "16{0:03d}")
    config.set("main", "host", "0.0.0.0")
    args.k.sort()
    config.set("main", "topics", args.k)
    config.add_section("www")
    config.set("www", "corpus_name", "Deafult")
    config.set("www", "icons", "link")
    config.add_section("logging")
    config.set("logging","path","logs/%s/{0}.log" % corpus_name)


    if args.htrc:
        config.set("main","label_module","extensions.htrc")
        config.set("www","corpus_name","HTRC Data Capsule")
        config.set("www","doc_title_format",'<a href="{1}">{0}</a>')
        config.set("www","doc_url_format", 'http://hdl.handle.net/2027/{0}')
        if args.corpus_type == 'page':
            config.set("www", "icons", "htrc,htrcbook,link")
        else:
            config.set("www", "icons", "htrc,link")

    configfile = corpus_name + ".ini"
    config_i = 0
    while os.path.exists(configfile):
        configfile = corpus_name + ".%d.ini" % config_i
        config_i += 1

    print "\nWriting configuration file", configfile
    with open(configfile, "wb") as configfh:
        config.write(configfh)
    
    if args.dry_run:
        print "\nTIP: Dry run, only initalizing corpus object and config file."
        print "     Next prepare the corpus using:"
        print "python corpus_prep.py", configfile
    else:
        print "\nTIP: launch the topic explorer with:"
        print "python launch.py", configfile
