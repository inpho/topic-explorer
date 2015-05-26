from ConfigParser import RawConfigParser as ConfigWriter
from ConfigParser import SafeConfigParser as ConfigParser
from ConfigParser import NoOptionError
import multiprocessing
import os.path

from vsm.corpus import Corpus
from vsm.model.lda import LDA

from topicexplorer.lib.util import bool_prompt

def build_models(corpus, corpus_filename, model_path, context_type, krange, 
                 n_iterations=200, n_proc=2, seed=None):

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
        m = LDA(corpus, context_type, K=k, multiprocessing=True, n_proc=n_proc,
                seed_or_seeds=seeds)
        m.train(n_iterations=n_iterations)
        m.save(basefilename.format(k))

    return basefilename

def continue_training(model_pattern, krange, n_iterations=200):
    for k in krange:
        m = LDA.load(model_pattern.format(k))

        print "Continue training model for k={0} Topics".format(k)
        m.train(n_iterations=n_iterations)

        # save new file
        basefilename = model_pattern.replace(
            "-{orig}.npz".format(orig=(m.iteration - n_iterations)),
            "-{new}.npz".format(new=m.iteration))
        m.save(basefilename.format(k))

    return basefilename

def main(args):
    config = ConfigParser()
    config.read(args.config_file)
    corpus_filename = config.get("main", "corpus_file")
    model_path = config.get("main", "path")

    if args.k is None:
        if config.get("main", "topics"):
            args.k = eval(config.get("main", "topics"))

        while args.k is None:
            ks = raw_input("Number of Topics [Default '20 40 60 80']: ")
            try:
                if ks:
                    args.k = [int(n) for n in ks.split()]
                elif not ks.strip():
                    args.k = range(20,100,20) 

                if args.k:
                    print "\nTIP: number of topics can be specified with argument '-k N N N ...':"
                    print "         vsm train %s -k %s\n" %\
                             (args.config_file, ' '.join(map(str, args.k)))
            except ValueError:
                print "Enter valid integers, separated by spaces!"
        
    
    if args.iter is None:
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
        print "         vsm train --iter %d %s\n" % (args.iter, args.config_file)


    try:
        model_pattern = config.get("main", "model_pattern")
    except NoOptionError:
        model_pattern = None

    if model_pattern is not None and\
        bool_prompt("Existing model found. Continue training?", default=True):
        # continue training
        model_pattern = continue_training(model_pattern, args.k, args.iter)

    else:
        # build a new model
        corpus = Corpus.load(corpus_filename)
    
        ctxs = corpus.context_types
        ctxs = sorted(ctxs, key=lambda ctx: len(corpus.view_contexts(ctx)))
        if args.context_type not in ctxs:
            while args.context_type not in ctxs:
                contexts = ctxs[:]
                contexts[0] = contexts[0].upper()
                contexts = '/'.join(contexts)
                args.context_type = raw_input("Select a context type [%s] : " % contexts)
                if args.context_type.strip() == '':
                    args.context_type = ctxs[0]
                if args.context_type == ctxs[0].upper():
                    args.context_type = ctxs[0]
    
            print "\nTIP: context type can be specified with argument '--context-type TYPE':"
            print "         vsm train --context-type %s %s\n" % (args.context_type, args.config_file)
    
    
        print "\nTIP: This configuration can be automated as:"
        print "         vsm train %s --iter %d --context-type %s -k %s\n" %\
            (args.config_file, args.iter, args.context_type, 
                ' '.join(map(str, args.k)))
    
        if args.processes < 0:
            args.processes = multiprocessing.cpu_count() + args.processes
    
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

