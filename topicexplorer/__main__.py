#!/usr/bin/env python
import argparse
from argparse import ArgumentParser
from ConfigParser import RawConfigParser as ConfigParser
import os.path

from topicexplorer import init, prep, train, server, launch, notebook, demo
from topicexplorer.lib.util import is_valid_filepath

def main():
    parser = ArgumentParser()
    parsers = parser.add_subparsers(help="select a command")

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
    launch.populate_parser(parser_launch)
    parser_launch.set_defaults(func="launch")

    # Serve Parser
    parser_serve = parsers.add_parser('serve', 
        help="Serve a single LDA model, helper for `vsm launch`,"+
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
    
    args = parser.parse_args()

    if args.func == 'init':
        args.config_file = init.main(args)
        
        print "\nTIP: Only initalizing corpus object and config file."
        print "     Next prepare the corpus using:"
        print "         vsm prep", args.config_file
        print "     Or skip directly to training LDA models using:"
        print "         vsm train", args.config_file

    elif args.func == 'prep':
        prep.main(args)
        
        print "\nTIP: Train the LDA models with:"
        print "         vsm train", args.config_file

    elif args.func == 'train':
        train.main(args)
        
        print "\nTIP: launch the topic explorer with:"
        print "         vsm launch", args.config_file
        print "     or the notebook server with:"
        print "         vsm notebook", args.config_file

    elif args.func == 'launch':
        launch.main(args)

    elif args.func == 'serve':
        server.main(args)

    elif args.func == 'notebook':
        notebook.main(args)

    elif args.func == 'demo':
        demo.main()

if __name__ == '__main__':
    main()
