"""
Train topic models on a corpus using Latent Dirichlet Allocation.

Topic Modeling
----------------

Topic models represent documents as mixtures of topics, which correspond to
common themes in the collection. The topic model is trained by an algorithm that
finds latent (hidden) relationships among the documents. Topic modeling is an
*unsupervised* learning process: there is no human specification of the content
of the topics. 

The number of topics is specified manually. With the Topic Explorer, we train 
multiple models with different numbers of topics. Each model shows different
levels of detail in the documents. A model with more topics will, in general,
show finer details. These models can be compared using the |topic map
visualization|_.

Each topic is a probability distribution over all the words in a corpus. Each
document is represented as a probability distribution over all the topics
inferred from the corpus. These two matrices (*word-topic* and
*topic-document*) represent the results of a topic model.

Running the topic model on the same text with the same parameters does not
guarantee the same results due to the probabilistic nature of the inference
process. In order to guarantee the same results across different runs over the
same text, the |seed parameter| must be set to the same number.

.. seealso::
    `Probabilistic Topic Models`_ (Blei 2012)
        Review of topic modeling.
    `InPhO Topic Explorer - The HTRC 1315 Hypershelf`_
        Video demonstrating topic modeling using the Topic Explorer.

.. |topic map visualization| replace::
    *topic map visualization* in ``topicexplorer launch``
.. _topic map visualization:
    launch.html#topic-map
.. |seed parameter| replace:: ``--seed`` parameter
.. _seed parameter: #random-seed-seed

.. _Probabilistic Topic Models:
    http://www.cs.columbia.edu/~blei/papers/Blei2012.pdf
.. _InPhO Topic Explorer - The HTRC 1315 Hypershelf:
    https://www.youtube.com/watch?v=QAPKCyA4uOc

Command Line Arguments 
------------------------

Number of Topics (``-k``)
'''''''''''''''''''''''''''
Select the number of topics in the model. Multiple numbers can be chosen to
train multiple models for comparison.

**Default:** ``-k 20 40 60 80``


Number of Iterations (``--iter``)
'''''''''''''''''''''''''''''''''''
Select the number of iterations to train each model.

**Default:** ``--iter 200``


Number of Processes (``-p``)
''''''''''''''''''''''''''''''
Select the number of processes to use. Defaults to using a single process.
Multi-core machines can use more processes to accelerate training.

**Default:** ``-p 1``


Random Seed (``--seed``)
''''''''''''''''''''''''''
Select the random seed to initialize the model.

The topic model is trained using a *pseudo-random number generator*. These
number generators appear random, but use long patterns. The seed tells the
pattern where to start. Using the same seed will cause the generator to use the
same numbers, and therefore generate the same topic models.

**Default:** a random integer is generated.


Rebuild models (``--rebuild``)
''''''''''''''''''''''''''''''''
If there are existing models for the specified values of ``-k``, retrain them
with ``--iter`` iterations.

``--rebuild`` cannot be used with ``--continue``.


Continue models (``--continue``)
''''''''''''''''''''''''''''''''''
If there are existing models for the specified values of ``-k``, train them for
an additional ``--iter`` iterations.

``--continue`` cannot be used with ``--rebuild``.



Quiet Mode (``-q``)
'''''''''''''''''''''
Suppresses all user input requests. Uses default values unless otherwise
specified by other argument flags. Very useful for scripting automated
pipelines.

"""
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import input
from builtins import map
from builtins import range

from configparser import NoOptionError
import os.path

import topicexplorer.config
from topicexplorer.lib.util import bool_prompt, int_prompt, is_valid_configfile


def build_models(corpus, corpus_filename, model_path, context_type, krange,
                 n_iterations=200, n_proc=1, seed=None, dry_run=False):
    basefilename = os.path.basename(corpus_filename).replace('.npz', '')
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
            print("Training model for k={0} Topics with {1} Processes".format(k, n_proc))
            m = LDA(corpus, context_type, K=k, multiprocessing=(n_proc > 1),
                    seed_or_seeds=seeds, n_proc=n_proc)
            m.train(n_iterations=n_iterations)
            m.save(basefilename.format(k))
            print(" ")

    return basefilename


def continue_training(model_pattern, krange, total_iterations=200, n_proc=1,
                      dry_run=False):
    from vsm.model.lda import LDA
    for k in krange:
        m = LDA.load(model_pattern.format(k), multiprocessing=(n_proc > 1))
        try:
            n_proc = m.n_proc
        except AttributeError:
            n_proc = 1

        # for some reason, the value of m.iteration is a reference, not
        # explicit. Filed error in vsm: https://github.com/inpho/vsm/issues/144
        orig_iterations = int(m.iteration)
        print("Continue training {0}-topic model ({1} => {2} iterations, {3} processes)".format(
            k, orig_iterations, total_iterations, n_proc))

        basefilename = model_pattern.replace(
            "-{orig}.npz".format(orig=orig_iterations),
            "-{new}.npz".format(new=total_iterations))

        if not dry_run:
            m.train(n_iterations=total_iterations - orig_iterations)
            m.save(basefilename.format(k))
            print(" ")

    return basefilename

def cluster(n_clusters, config_file):
    from .cluster import dimensionReduce
    dimension_reduce_model = dimensionReduce(config_file)

    dimension_reduce_model.fit_isomap()  
    dimension_reduce_model.fit_kmeans(int(n_clusters))

    print("writing model files for Isomap and kmeans\n")
    config = topicexplorer.config.read(config_file)
    corpus_filename = config.get("main", "corpus_file")
    filename = '.'.join(corpus_filename.split('.')[:-1]) + '-cluster.csv'

    config.set("main", "cluster", filename)
    with open(config_file, "w") as configfh:
        config.write(configfh)
    dimension_reduce_model.write(config.get("main", "cluster"))

    return filename
    
    

def main(args):
    if args.cluster:
        cluster(args.cluster, args.config_file)
        return

    config = topicexplorer.config.read(args.config_file)
    corpus_filename = config.get("main", "corpus_file")
    model_path = config.get("main", "path")

    if config.getboolean("main", "sentences"):
        from vsm.extensions.ldasentences import CorpusSent as Corpus
    else:
        from vsm.corpus import Corpus

    if args.k is None:
        #TODO: Clean up default topic numbers
        try:
            if config.get("main", "topics"):
                default = ' '.join(map(str, eval(config.get("main", "topics"))))
                if args.quiet:
                    args.k = [int(n) for n in default.split()]
            else:
                raise NoOptionError('main', 'topics')
        except NoOptionError:
            default = ' '.join(map(str, range(20, 100, 20)))

        while args.k is None:
            ks = input("Number of Topics [Default '{0}']: ".format(default))
            try:
                if ks:
                    args.k = [int(n) for n in ks.split()]
                elif not ks.strip():
                    args.k = [int(n) for n in default.split()]

                if args.k:
                    print("\nTIP: number of topics can be specified with argument '-k N N N ...':")
                    print("         topicexplorer train %s -k %s\n" %\
                        (args.config_file, ' '.join(map(str, args.k))))
            except ValueError:
                print("Enter valid integers, separated by spaces!")

    if args.processes < 0:
        import multiprocessing
        args.processes = multiprocessing.cpu_count() + args.processes

    print("Loading corpus... ")
    corpus = Corpus.load(corpus_filename)

    try:
        model_pattern = config.get("main", "model_pattern")
    except NoOptionError:
        model_pattern = None

    if (model_pattern is not None and not args.rebuild and (args.quiet or args.cont or
            bool_prompt("""Existing topic models found. You can continue training or start a new model. 
Do you want to continue training your existing models? """, default=True))):

        from vsm.model.lda import LDA
        m = LDA.load(model_pattern.format(args.k[0]),
                     multiprocessing=args.processes > 1,
                     n_proc=args.processes)

        if args.iter is None and not args.quiet:    # pragma: no cover
            args.iter = int_prompt("Total number of training iterations:",
                                   default=int(m.iteration * 1.5), min=m.iteration)

            print("\nTIP: number of training iterations can be specified with argument '--iter N':")
            print("         topicexplorer train --iter %d %s\n" % (args.iter, args.config_file))
        elif args.iter is None and args.quiet:      # pragma: no cover
            args.iter = int(m.iteration * 1.5)

        del m

        # if the set changes, build some new models and continue some old ones

        config_topics = eval(config.get("main", "topics"))
        if args.k != config_topics:
            new_models = set(args.k) - set(config_topics)
            continuing_models = set(args.k) & set(config_topics)

            build_models(corpus, corpus_filename, model_path,
                         config.get("main", "context_type"),
                         new_models, n_iterations=args.iter,
                         n_proc=args.processes, seed=args.seed,
                         dry_run=args.dry_run)

            model_pattern = continue_training(model_pattern, continuing_models,
                                              args.iter, n_proc=args.processes,
                                              dry_run=args.dry_run)

        else:
            model_pattern = continue_training(model_pattern, args.k, args.iter,
                                              n_proc=args.processes, 
                                              dry_run=args.dry_run)
    else:
        # build a new model
        if args.iter is None and not args.quiet:    # pragma: no cover
            args.iter = int_prompt("Number of training iterations:", default=200)

            print("\nTIP: number of training iterations can be specified with argument '--iter N':")
            print("         topicexplorer train --iter %d %s\n" % (args.iter, args.config_file))
        elif args.iter is None and args.quiet:      # pragma: no cover
            args.iter = 200

        # TODO: if only one context_type, make it just the one context type.
        ctxs = corpus.context_types
        if len(ctxs) == 1:
            args.context_type = ctxs[0]
        else:
            ctxs = sorted(ctxs, key=lambda ctx: len(corpus.view_contexts(ctx)))
            if args.context_type not in ctxs:
                while args.context_type not in ctxs:
                    contexts = ctxs[:]
                    contexts[0] = contexts[0].upper()
                    contexts = '/'.join(contexts)
                    args.context_type = input("Select a context type [%s] : " % contexts)
                    if args.context_type.strip() == '':
                        args.context_type = ctxs[0]
                    if args.context_type == ctxs[0].upper():
                        args.context_type = ctxs[0]
    
                print("\nTIP: context type can be specified with argument '--context-type TYPE':")
                print("         topicexplorer train --context-type %s %s\n" % (args.context_type, args.config_file))


        print("\nTIP: This configuration can be automated as:")
        print("         topicexplorer train %s --iter %d --context-type %s -k %s\n" %\
            (args.config_file, args.iter, args.context_type, 
                ' '.join(map(str, args.k))))
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
        if config.has_option("main", "cluster"):
            cluster_path = config.get("main", "cluster", fallback=None)
            config.remove_option("main", "cluster")
            try:
                if cluster_path:
                    os.remove(cluster_path)
            except (OSError, IOError):
                # fail silently on IOError
                pass


        with open(args.config_file, "w") as configfh:
            config.write(configfh)


def populate_parser(parser):
    import argparse
    parser.add_argument("config_file", help="Path to Config",
                        type=lambda x: is_valid_configfile(parser, x))
    parser.add_argument("-k", nargs='+',
                        help="K values to train upon", type=int)
    parser.add_argument('--iter', type=int,
                        help="Number of training iterations")
    parser.add_argument("-p", "--processes", default=1, type=int,
                        help="Number of CPU cores for training [Default: 1]")
    parser.add_argument("--context-type", dest='context_type',
                        help=argparse.SUPPRESS)
    parser.add_argument("--seed", default=None, type=int,
                        help="Random seed for topic modeling [Default: None]")
    parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                        help="Run code without training models")
    parser.add_argument('--rebuild', action='store_true')
    parser.add_argument('--continue', dest='cont', action='store_true')
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('--cluster', type=int,
                        help=argparse.SUPPRESS)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
