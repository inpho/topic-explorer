from ConfigParser import RawConfigParser as ConfigWriter
from ConfigParser import SafeConfigParser as ConfigParser
import multiprocessing
import os.path

from vsm.corpus import Corpus
from vsm.model.lda import LDA

def build_models(corpus, corpus_filename, model_path, context_type, krange, n_iterations=200,
                 n_proc=2, seed=None):

    basefilename = os.path.basename(corpus_filename).replace('.npz','')
    basefilename += "-LDA-K%s-%s-%d.npz" % ('{0}', context_type, n_iterations)
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
        m = LDA(corpus, context_type, K=k, multiprocessing=True)
        m.train(n_iterations=n_iterations, n_proc=n_proc, seeds=seeds)
        m.save(basefilename.format(k))

    return basefilename

def main(args):
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

    config = ConfigParser()
    config.read(args.config_file)
    corpus_filename = config.get("main", "corpus_file")
    model_path = config.get("main", "path")

    corpus = Corpus.load(corpus_filename)
    # TODO: Prompt for context_type
    ctxs = corpus.context_types
    ctxs = sorted(ctxs, key=lambda ctx: len(corpus.view_contexts(ctx)))
    while args.context_type not in ctxs:
        contexts = ctxs[:]
        contexts[0] = contexts[0].upper()
        contexts = '/'.join(contexts)
        args.context_type = raw_input("Select a context type [%s] : " % contexts)
        if args.context_type.strip() == '':
            args.context_type = ctxs[0]
        if args.context_type == ctxs[0].upper():
            args.context_type = ctxs[0]
    
    model_pattern = build_models(corpus, corpus_filename, model_path, 
                                 args.context_type, args.k,
                                 n_iterations=args.iter,
                                 n_proc=args.processes, seed=args.seed)

    config.set("main", "model_pattern", model_pattern)
    config.set("main", "context_type", args.context_type)
    args.k.sort()
    config.set("main", "topics", str(args.k))
    
    with open(args.config_file, "wb") as configfh:
        config.write(configfh)

