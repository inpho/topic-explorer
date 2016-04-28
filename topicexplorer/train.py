from ConfigParser import RawConfigParser as ConfigWriter
from ConfigParser import SafeConfigParser as ConfigParser
from ConfigParser import NoOptionError
import os.path

from topicexplorer.lib.util import bool_prompt, int_prompt, is_valid_configfile

def build_models(corpus, corpus_filename, model_path, context_type, krange, 
                 n_iterations=200, n_proc=1, seed=None, dry_run=False):
    basefilename = os.path.basename(corpus_filename).replace('.npz','')
    basefilename += "-LDA-K%s-%s-%d.npz" % ('{0}', context_type, n_iterations)
    basefilename = os.path.join(model_path, basefilename)

    if n_proc == 1 and type(seed) == int:
        seeds = seed
        fileparts = basefilename.split('-')
        fileparts.insert(-1, str(seed))
        basefilename = '-'.join(fileparts)
    elif type(seed) == int:
        seeds = [seed + p for p in range(n_proc)]
        fileparts = basefilename.split('-')
        fileparts.insert(-1, str(seed))
        basefilename = '-'.join(fileparts)
    else:
        seeds = None

    if not dry_run:
        from vsm.model.lda import LDA
        for k in krange:
            print "Training model for k={0} Topics with {1} Processes"\
                .format(k, n_proc)
            m = LDA(corpus, context_type, K=k, multiprocessing=(n_proc > 1),
                    seed_or_seeds=seeds)
            m.train(n_iterations=n_iterations)
            m.save(basefilename.format(k))
            print " "

    return basefilename

def continue_training(model_pattern, krange, total_iterations=200, n_proc=1):
    from vsm.model.lda import LDA
    for k in krange:
        m = LDA.load(model_pattern.format(k), multiprocessing=(n_proc > 1))

        print "Continue training model for k={0} Topics".format(k)
        orig_iterations = m.iteration
        m.train(n_iterations=total_iterations - orig_iterations)

        # save new file
        basefilename = model_pattern.replace(
            "-{orig}.npz".format(orig=orig_iterations),
            "-{new}.npz".format(new=total_iterations))
        m.save(basefilename.format(k))
        print " "

    return basefilename

def main(args):

    config = ConfigParser({"sentences": "False"})
    config.read(args.config_file)
    corpus_filename = config.get("main", "corpus_file")
    model_path = config.get("main", "path")

    if config.getboolean("main", "sentences"):
        from vsm.extensions.ldasentences import CorpusSent as Corpus
    else:
        from vsm.corpus import Corpus

    if args.k is None:
        try:
            if config.get("main", "topics"):
                default = ' '.join(map(str, eval(config.get("main", "topics"))))
            else:
                raise NoOptionError
        except NoOptionError:
            default = ' '.join(map(str, range(20,100,20)))

        while args.k is None:
            ks = raw_input("Number of Topics [Default '{0}']: ".format(default))
            try:
                if ks:
                    args.k = [int(n) for n in ks.split()]
                elif not ks.strip():
                    args.k = [int(n) for n in default.split()]

                if args.k:
                    print "\nTIP: number of topics can be specified with argument '-k N N N ...':"
                    print "         vsm train %s -k %s\n" %\
                             (args.config_file, ' '.join(map(str, args.k)))
            except ValueError:
                print "Enter valid integers, separated by spaces!"
        
    if args.processes < 0:
        import multiprocessing
        args.processes = multiprocessing.cpu_count() + args.processes

    print "Loading corpus... "
    corpus = Corpus.load(corpus_filename)

    try:
        model_pattern = config.get("main", "model_pattern")
    except NoOptionError:
        model_pattern = None

    if model_pattern is not None and\
        bool_prompt("Existing models found. Continue training?", default=True):

        from vsm.model.lda import LDA
        m = LDA.load(model_pattern.format(args.k[0]),
                     multiprocessing=args.processes > 1,
                     n_proc=args.processes)

        if args.iter is None:
            args.iter = int_prompt("Total number of training iterations:",
                                   default=int(m.iteration*1.5), min=m.iteration)
    
            print "\nTIP: number of training iterations can be specified with argument '--iter N':"
            print "         vsm train --iter %d %s\n" % (args.iter, args.config_file)

        del m

        # if the set changes, build some new models and continue some old ones

        config_topics = eval(config.get("main","topics"))
        if args.k != config_topics :
            new_models = set(args.k) - set(config_topics)
            continuing_models = set(args.k) & set(config_topics)
        
            build_models(corpus, corpus_filename, model_path, 
                                         config.get("main", "context_type"),
                                         new_models, n_iterations=args.iter,
                                         n_proc=args.processes, seed=args.seed)

            model_pattern = continue_training(model_pattern, continuing_models,
                                              args.iter, n_proc=args.processes)

        else:
            model_pattern = continue_training(model_pattern, args.k, args.iter,
                                              n_proc=args.processes)

    else:
        # build a new model
        if args.iter is None:
            args.iter = int_prompt("Number of training iterations:", default=200)
    
            print "\nTIP: number of training iterations can be specified with argument '--iter N':"
            print "         vsm train --iter %d %s\n" % (args.iter, args.config_file)
    
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
        model_pattern = build_models(corpus, corpus_filename, model_path, 
                                     args.context_type, args.k,
                                     n_iterations=args.iter,
                                     n_proc=args.processes, seed=args.seed,
                                     dry_run=args.dry_run)
    config.set("main", "model_pattern", model_pattern)
    if args.context_type:
        # test for presence, since continuing doesn't require context_type
        config.set("main", "context_type", args.context_type)
    args.k.sort()
    config.set("main", "topics", str(args.k))
    
    if not args.dry_run:
        with open(args.config_file, "wb") as configfh:
            config.write(configfh)

def populate_parser(parser):
    parser.add_argument("config_file", help="Path to Config",
        type=lambda x: is_valid_configfile(parser, x))
    parser.add_argument("--context-type", dest='context_type',
        help="Level of corpus modeling, prompts if not set")
    parser.add_argument("-p", "--processes", default=1, type=int,
        help="Number of CPU cores for training [Default: 1]")
    parser.add_argument("--seed", default=None, type=int,
        help="Random seed for topic modeling [Default: None]")
    parser.add_argument("-k", nargs='+',
        help="K values to train upon", type=int)
    parser.add_argument('--iter', type=int,
        help="Number of training iterations")
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
        help="Run code without training models")


if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)

