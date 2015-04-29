#!/usr/bin/env python
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
    parser_init.add_argument("corpus_path", help="Path to Corpus",
        type=lambda x: is_valid_filepath(parser_init, x))
    parser_init.add_argument("config_file", nargs="?", 
        help="Path to Config [optional]")
    parser_init.add_argument("--model-path", dest="model_path",
        help="Model Path [Default: [corpus_path]/../models]")
    parser_init.add_argument("--rebuild", action="store_true")
    parser_init.add_argument("--htrc", action="store_true")
    parser_init.set_defaults(func="init")
    
    # Prep Parser
    parser_prep = parsers.add_parser('prep', help="Prep the corpus")
    parser_prep.add_argument("config_file", help="Path to Config",
        type=lambda x: is_valid_filepath(parser_prep, x))
    parser_prep.add_argument("--htrc", action="store_true")
    parser_prep.add_argument("--stopword-file", dest="stopword_file",
        help="File with custom stopwords")
    parser_prep.add_argument("--lang", nargs='+', help="Languages to stoplist")
    parser_prep.set_defaults(func="prep")

    # Train Parser
    parser_train = parsers.add_parser('train', help="Train the LDA models")
    parser_train.add_argument("config_file", help="Path to Config",
        type=lambda x: is_valid_filepath(parser_train, x))
    parser_train.add_argument("--context-type", dest='context_type',
        help="Level of corpus modeling, prompts if not set")
    parser_train.add_argument("-p", "--processes", default=2, type=int,
        help="Number of CPU cores for training [Default: 2]")
    parser_train.add_argument("--seed", default=None, type=int,
        help="Random seed for topic modeling [Default: None]")
    parser_train.add_argument("-k", nargs='+',
        help="K values to train upon", type=int)
    parser_train.add_argument('--iter', type=int,
        help="Number of training iterations")
    parser_train.set_defaults(func="train")
    
    # Launch Parser
    parser_launch = parsers.add_parser('launch', help="Serve the trained LDA models")
    parser_launch.add_argument('config_file', help="Configuration file path",
        type=lambda x: is_valid_filepath(parser_launch, x))
    parser_launch.add_argument('--no-browser', dest='browser', action='store_false')
    parser_launch.set_defaults(func="launch")

    # Serve Parser
    parser_serve = parsers.add_parser('serve', 
        help="Serve a single LDA model, helper for `vsm launch`,"+
             "rarely called directly")
    parser_serve.add_argument('config', type=lambda x: is_valid_filepath(parser_serve, x),
        help="Configuration file path")
    parser_serve.add_argument('-k', type=int, required=True,
        help="Number of Topics")
    parser_serve.add_argument('-p', dest='port', type=int, 
        help="Port Number", default=None)
    parser_serve.add_argument('--host', default=None, help='Hostname')
    parser_serve.add_argument('--ssl', action='store_true',
        help="Use SSL (must specify certfile, keyfile, and ca_certs in config)")
    parser_serve.add_argument('--ssl-certfile', dest='certfile', nargs="?",
        const='server.pem', default=None,
        type=lambda x: is_valid_filepath(parser_serve, x),
        help="SSL certificate file")
    parser_serve.add_argument('--ssl-keyfile', dest='keyfile', default=None,
        type=lambda x: is_valid_filepath(parser_serve, x),
        help="SSL certificate key file")
    parser_serve.add_argument('--ssl-ca', dest='ca_certs', default=None,
        type=lambda x: is_valid_filepath(parser_serve, x),
        help="SSL certificate authority file")
    parser_serve.set_defaults(func="serve")
   
    # Notebook Parser
    parser_nb = parsers.add_parser('notebook', 
        help="Create a set of IPython Notebooks")
    parser_nb.add_argument("config_file", help="Path to Config File")
    parser_nb.add_argument('--no-launch', dest='launch', action='store_false')
    parser_nb.set_defaults(func="notebook")

    # Demo Parser
    parser_nb = parsers.add_parser('demo', 
        help="Download and run the AP demo")
    parser_nb.set_defaults(func="demo")
    
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
