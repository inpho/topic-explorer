"""
Simple Full-text Topic Explorer
"""

import os
import os.path

from vsm.corpus import Corpus
from vsm.corpus.util.corpusbuilders import coll_corpus, dir_corpus, toy_corpus
from vsm.model.ldacgsmulti import LdaCgsMulti as LDA
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer

def build_corpus(corpus_path, model_path, nltk_stop=True, stop_freq=1,
    context_type='document'):
    if os.path.isfile(corpus_path):
        print "Building toy corpus, each line is a document"
        c = toy_corpus(corpus_path, nltk_stop=nltk_stop, stop_freq=stop_freq,
                       context_type=context_type)
    elif os.path.isdir(corpus_path):
        contents = os.listdir(corpus_path)
        count_dirs = filter(os.path.isdir, contents)
        count_files = filter(os.path.isfile, contents)

        if count_dirs > count_files:
            print "Building collection corpus, each folder is a document"
            c = coll_corpus(corpus_path, nltk_stop=nltk_stop,
                            stop_freq=stop_freq, context_type=context_type)
        else:
            print "Building dir corpus, each file is a document"
            c = dir_corpus(corpus_path, nltk_stop=nltk_stop,
                           stop_freq=stop_freq, chunk_name=context_type)

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

def build_models(corpus_filename, model_path, krange, 
                 corpus_type='document', n_iterations=200):

    corpus = Corpus.load(corpus_filename)
    basefilename = os.path.basename(corpus_filename).replace('.npz','')
    basefilename += "-LDA-K%s-%s-%d.npz" % ('{0}', corpus_type, n_iterations)
    basefilename = os.path.join(model_path, basefilename)

    for k in krange:
        print "Training model for k={0} Topics".format(k)
        m = LDA(corpus, corpus_type, K=k)
        m.train(n_iterations=n_iterations)
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
    parser.add_argument("-k", nargs='+',
        help="K values to train upon", type=int)
    parser.add_argument('--iter', type=int, default=200,
        help="Number of training iterations [Default: 200]")
    args = parser.parse_args()

    if args.model_path is None:
        args.model_path = os.path.join(args.corpus_path, '../models/')
    if not os.path.exists(args.model_path):
        os.makedirs(args.model_path)

    if args.k is None:
        args.k = range(120,0,-20)
    

    corpus_filename = build_corpus(args.corpus_path, args.model_path, 
                                   stop_freq=5)
    model_pattern = build_models(corpus_filename, args.model_path, args.k,
                 n_iterations=args.iter)


    config = ConfigParser()
    config.add_section("main")
    config.set("main", "path", args.model_path)
    config.set("main", "corpus_file", corpus_filename)
    config.set("main", "context_type", "document")
    config.set("main", "model_pattern", model_pattern)
    config.set("main", "port", "16{0:03d}")
    args.k.sort()
    config.set("main", "topics", args.k)
    config.add_section("www")
    config.set("www", "corpus_name", "Deafult")
    config.set("www", "icons", "link")

    if args.htrc:
        config.set("main","label_module","extensions.htrc")
        config.set("www","corpus_name","HTRC Data Capsule")
        config.set("www","doc_title_format",'<a href="{1}">{0}</a>')
        config.set("www","doc_url_format", 'http://hdl.handle.net/2027/{0}')
        config.set("www", "icons", "htrc,link")

    configfile = "config.ini"
    config_i = 0
    while os.path.exists(configfile):
        configfile = "config.%d.ini" % config_i
        config_i += 1

    print "Writing configuration file", configfile
    with open(configfile, "wb") as configfh:
        config.write(configfh)
