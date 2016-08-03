#!/usr/bin/env python
"""
`topicexplorer.__main__`

This file defines the master script for the Topic Explorer CLI.
The general usage pattern is to create subcommands through new modules
in the same package - such as `topicexplorer.init`,
`topicexplorer.prep`, `topicexplorer.train`, etc.

Each submodule defines a `populate_parser()` function which adds
command arguments to an `argparse.ArgumentParser` instance. The instance
is then added to the master `ArgumentParser` and a `func` keyword
is used to switch between the functionality defined by each module's
`main()` method.

In addition, `topicexplorer.__main__` defines the benchmark commands
for execution time and profiling.

"""

# Import the standard library modules
import argparse
from argparse import ArgumentParser
from ConfigParser import RawConfigParser as ConfigParser
import os.path
import warnings

from topicexplorer import (init, prep, train, server, notebook,
    demo, update, metadata)

from topicexplorer.lib.util import is_valid_filepath


class ArgumentParserError(Exception):
    """
    Skeleton class for use in `try` blocks.
    """
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    """
    Skeleton subclass of argparse.ArgumentParser to raise exceptions.
    """

    def error(self, message):
        raise ArgumentParserError(message)


def vsm():
    warning_msg = ("The `vsm` command has been replaced by `topicexplorer`.\n" +
                   "    `vsm` will be removed in the 1.0 release.\n" +
                   "See http://github.com/inpho/topic-explorer/issues/136.")
    warnings.warn(warning_msg, DeprecationWarning)

    # Force error to print
    print "WARNING: " + warning_msg
    import sys
    if sys.argv[0].endswith('vsm') and len(sys.argv) > 1:
        print "\nTIP: Use the following command instead:"
        print '    topicexplorer ' + ' '.join(sys.argv[1:]) + '\n'

    # Proceed while deprecated
    main()


def main():
    """
    The primary CLI function for the Topic Explorer.
    """
    # Create the master argparse object.
    parser = ThrowingArgumentParser()

    # Adding the benchmarks flags.
    benchmark_group = parser.add_mutually_exclusive_group()
    benchmark_group.add_argument('-t', '--time', help="Print execution time",
                                 action='store_true')
    benchmark_group.add_argument('-p', '--profile', help="""Profile the command.
    Optional filename saves results for use with snakeviz, pstats, or
    cprofilev. Automatically launches snakeviz, if installed.""",
                                 nargs='?', metavar='STATS_FILE')

    # Using add_subparsers(metavar) until argparse.SUPPRESS support is fixed.
    # See issue http://bugs.python.org/issue22848
    parsers = parser.add_subparsers(help="select a command",
                                    parser_class=ArgumentParser,
                                    metavar='{version,demo,update,init,prep,train,launch,notebook,metadata}')
    version_parser = parsers.add_parser('version', help="Print the version and exit")
    version_parser.set_defaults(func='version')

    # Init Parser
    parser_init = parsers.add_parser('init', help="Initialize the topic explorer")
    init.populate_parser(parser_init)
    parser_init.set_defaults(func="init")

    # Prep Parser
    parser_prep = parsers.add_parser('prep', help="Prep the corpus",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    prep.populate_parser(parser_prep)
    parser_prep.set_defaults(func="prep")

    # Train Parser
    parser_train = parsers.add_parser('train', help="Train the LDA models")
    train.populate_parser(parser_train)
    parser_train.set_defaults(func="train")

    # Launch Parser
    parser_launch = parsers.add_parser('launch', help="Serve the trained LDA models")
    server.populate_parser(parser_launch)
    parser_launch.set_defaults(func="launch")

    # Serve Parser
    parser_serve = parsers.add_parser('serve', 
        help="Serve a single LDA model, helper for `topicexplorer launch`," +
             "rarely called directly")
    server.populate_parser(parser_serve)
    parser_serve.set_defaults(func="serve")

    # Notebook Parser
    parser_nb = parsers.add_parser('notebook',
                                   help="Create a set of IPython Notebooks")
    notebook.populate_parser(parser_nb)
    parser_nb.set_defaults(func="notebook")

    # Demo Parser
    parser_demo = parsers.add_parser('demo',
                                     help="Download and run the AP demo")
    parser_demo.set_defaults(func="demo")

    # Update Parser
    parser_update = parsers.add_parser('update',
                                       help="Update the Topic Explorer")
    parser_update.set_defaults(func="update")
    
    # Metadata Parser
    parser_metadata = parsers.add_parser('metadata', 
        help="Add spaces before unicode chars")
    metadata.populate_parser(parser_metadata)
    parser_metadata.set_defaults(func="metadata")

    # fancy arg validation for manually injecting tempfile to profile arg 
    try:
        try:
            args = parser.parse_args()
        except ArgumentParserError as e:
            import sys
            new_args = sys.argv[1:]
            try:
                # If the error was thrown by the '-p' argument not having a
                # valid file, fix by manually injecting a nargs break
                profile = new_args.index('-p')

                if (len(new_args) > (profile + 1) and
                        new_args[profile + 1] in parsers.choices.keys()):
                    new_args.insert(profile + 1, '-')
                    args = parser.parse_args(new_args)
                else:
                    raise e
            except ValueError:
                raise e
    except ArgumentParserError as e:
        import sys
        # Check to see if error occurs with a subparser and cause the exception
        # to arise from the subparser instead
        for p in parsers.choices.keys():
            if p in sys.argv[1:]:
                subargs_idx = sys.argv.index(p) + 1
                subargs = sys.argv[subargs_idx:]
                subparser = locals()['parser_' + p]
                # this might cause an error in the subparser, in which case
                # we actually want to show that error first
                args = subparser.parse_args(subargs)

        # Use the default error mechanism for the master parser.
        # If the code gets here, it means the error was not in a subparser
        ArgumentParser.error(parser, e.message)

    if args.profile:
        if args.profile == '-':
            import tempfile
            temphandle, args.profile = tempfile.mkstemp(suffix='.prof', prefix='vsm.')
            print "Saving benchmark data to", args.profile

        from profilehooks import profile

        def benchmark(fn):
            return profile(fn, immediate=True, filename=args.profile, stdout=None)

    elif args.time:
        from profilehooks import timecall

        def benchmark(fn):
            return timecall(fn, immediate=False)
    else:
        def benchmark(fn):
            return fn

    if args.func == 'version':
        from topicexplorer.version import __pretty_version__
        print __pretty_version__,

    elif args.func == 'init':
        args.config_file = benchmark(init.main)(args)

        print "\nTIP: Only initalizing corpus object and config file."
        print "     Next prepare the corpus using:"
        print "         topicexplorer prep", args.config_file
        print "     Or skip directly to training LDA models using:"
        print "         topicexplorer train", args.config_file

    elif args.func == 'prep':
        benchmark(prep.main)(args)

        print "\nTIP: Train the LDA models with:"
        print "         topicexplorer train", args.config_file

    elif args.func == 'train':
        benchmark(train.main)(args)

        if not args.dry_run:
            print "\nTIP: launch the topic explorer with:"
            print "         topicexplorer launch", args.config_file
            print "     or the notebook server with:"
            print "         topicexplorer notebook", args.config_file

    elif args.func == 'launch' or args.func == 'serve':
        # Note that we are only benchmarking the creation process - obviously
        # benches of the serve process will take longer
        app = benchmark(server.create_app)(args)
        server.main(args, app)


    elif args.func == 'notebook':
        benchmark(notebook.main)(args)

    elif args.func == 'demo':
        benchmark(demo.main)(args)

    elif args.func == 'update':
        benchmark(update.main)(args)

    elif args.func == 'metadata':
        benchmark(metadata.main)(args)

    if args.profile:
        try:
            import snakeviz.cli
            print "\n\n"
            snakeviz.cli.main([args.profile])
        except ImportError:
            print """\nSnakeviz is not installed. Install with `pip install snakeviz`,
            then run `snakeviz {}`.""".format(args.profile)


# Allow `__main__` to be called as a script.
if __name__ == '__main__':
    main()
