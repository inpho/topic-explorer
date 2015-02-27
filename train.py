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
from vsm.model.ldacgsmulti import LdaCgsMulti as LDA
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer

def build_corpus(corpus_path, model_path, nltk_stop=True, stop_freq=1,
    context_type='document', ignore=['.json','.log','.err','.pickle','.npz']):
    if os.path.isfile(corpus_path):
        print "Constructing toy corpus, each line is a document"
        c = toy_corpus(corpus_path, is_filename=True, nltk_stop=nltk_stop, 
                       stop_freq=stop_freq, context_type=context_type)
    elif os.path.isdir(corpus_path):
        contents = os.listdir(corpus_path)
        contents = [os.path.join(corpus_path,obj) for obj in contents 
            if not any([obj.endswith(suffix) for suffix in ignore])]
        count_dirs = len(filter(os.path.isdir, contents))
        count_files = len(filter(os.path.isfile, contents))

        print "Detected %d folders and %d files in %s" %\
            (count_dirs, count_files, corpus_path)

        if count_files > 0 and count_dirs == 0:
            print "Constructing directory corpus, each file is a document"
            c = dir_corpus(corpus_path, nltk_stop=nltk_stop,
                           stop_freq=stop_freq, chunk_name=context_type,
                           ignore=ignore)
        elif count_dirs > 0 and count_files == 0:
            print "Constructing collection corpus, each folder is a document"
            context_type='book'
            c = coll_corpus(corpus_path, nltk_stop=nltk_stop,
                            stop_freq=stop_freq, ignore=ignore)
        else:
            raise IOError("Invalid Path: empty directory")
    else:
        raise IOError("Invalid path")

    corpus_name = os.path.basename(corpus_path)
    if not corpus_name:
        corpus_name = os.path.basename(os.path.dirname(corpus_path))
    if nltk_stop and stop_freq:
        filename = '%s-nltk-en-freq%d.npz' % (corpus_name, stop_freq)
    elif stop_freq:
        filename = '%s-freq%d.npz' % (corpus_name, stop_freq)
    else:
        filename = '%s.npz' % corpus_name
    filename = os.path.join(model_path, filename)

    c.save(filename)
    return filename 

def build_models(corpus_filename, model_path, krange, n_iterations=200,
                 n_proc=2):

    corpus = Corpus.load(corpus_filename)
    if 'book' in corpus.context_types:
        corpus_type = 'book'
    else:
        corpus_type = 'document'

    basefilename = os.path.basename(corpus_filename).replace('.npz','')
    basefilename += "-LDA-K%s-%s-%d.npz" % ('{0}', corpus_type, n_iterations)
    basefilename = os.path.join(model_path, basefilename)


    for k in krange:
        print "Training model for k={0} Topics with {1} Processes"\
            .format(k, n_proc)
        m = LDA(corpus, corpus_type, K=k)
        m.train(n_iterations=n_iterations, n_proc=n_proc)
        m.save(basefilename.format(k))

    return basefilename

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ConfigParser import RawConfigParser as ConfigParser
    parser = ArgumentParser()
    parser.add_argument("corpus_path", help="Path to Corpus")
    parser.add_argument("--model-path", dest="model_path",
        help="Model Path [Default: [corpus_path]/../models]")
    parser.add_argument("--htrc", action="store_true")
    parser.add_argument("-p", "--processes", default=-2, type=int,
        help="Number of CPU cores for training [Default: total - 2]")
    parser.add_argument("-k", nargs='+',
        help="K values to train upon", type=int)
    parser.add_argument('--iter', type=int,
        help="Number of training iterations")
    parser.add_argument('--dry-run', action="store_true",
        help="Only create corpus object and config file, not models")
    args = parser.parse_args()

    if args.model_path is None:
        args.model_path = os.path.join(args.corpus_path, '../models/')
    if not os.path.exists(args.model_path):
        os.makedirs(args.model_path)

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
        print "python train.py --iter %d %s\n" % (args.iter, args.corpus_path)

    if args.processes < 0:
        args.processes = multiprocessing.cpu_count() + args.processes
    
    corpus_name = os.path.basename(args.corpus_path)
    if not corpus_name:
        corpus_name = os.path.basename(os.path.dirname(args.corpus_path))
    

    try:
        corpus_filename = build_corpus(args.corpus_path, args.model_path, 
                                       stop_freq=5)
    except IOError:
        print "ERROR: invalid path, please specify either:"
        print "  * a single plain-text file,"
        print "  * a folder of plain-text files, or"
        print "  * a folder of folders of plain-text files."
        print "\nExiting..."
        sys.exit(74)
    
    if args.dry_run:
        model_pattern = build_models(corpus_filename, args.model_path, list(),
                                     n_iterations=args.iter, n_proc=args.processes)
    else:
        model_pattern = build_models(corpus_filename, args.model_path, args.k,
                                     n_iterations=args.iter, n_proc=args.processes)

    corpus = Corpus.load(corpus_filename)
    if 'book' in corpus.context_types:
        corpus_type = 'book'
    else:
        corpus_type = 'document'

    config = ConfigParser()
    config.add_section("main")
    config.set("main", "path", args.model_path)
    config.set("main", "corpus_file", corpus_filename)
    config.set("main", "context_type", corpus_type)
    config.set("main", "model_pattern", model_pattern)
    config.set("main", "port", "16{0:03d}")
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
