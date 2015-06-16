from ConfigParser import RawConfigParser as ConfigParser
import os
import os.path
import shutil
import sys

from vsm.corpus import Corpus
from vsm.corpus.util.corpusbuilders import coll_corpus, dir_corpus, toy_corpus

from topicexplorer.lib import pdf, util
from topicexplorer.lib.util import prompt, is_valid_filepath

def get_corpus_filename(corpus_path, model_path, nltk_stop=False, stop_freq=1,
			context_type='document'):
    corpus_name = os.path.basename(corpus_path)
    if not corpus_name:
        corpus_name = os.path.basename(os.path.dirname(corpus_path))
    
    corpus_name.replace('-txt', '')

    if nltk_stop and stop_freq:
        filename = '%s-nltk-en-freq%d.npz' % (corpus_name, stop_freq)
    elif stop_freq:
        filename = '%s-freq%d.npz' % (corpus_name, stop_freq)
    else:
        filename = '%s.npz' % corpus_name
    return os.path.join(model_path, filename)


def build_corpus(corpus_path, model_path, nltk_stop=False, stop_freq=1,
    context_type='document', ignore=['.json','.log','.err','.pickle','.npz']):
   
    # pre-process PDF files
    if corpus_path[-4:] == '.pdf' or util.contains_pattern(corpus_path, '*.pdf'):
        if os.path.isdir(corpus_path):
            print "PDF files detected, extracting plaintext to", corpus_path + '-txt'
            if corpus_path.endswith('/'):
                corpus_path = corpus_path[:-1]
            pdf.main(corpus_path, corpus_path + '-txt')
            corpus_path += '-txt'
        else:
            print "PDF files detected, extracting plaintext to",\
                corpus_path.replace('.pdf','.txt')
            pdf.main(corpus_path)
            corpus_path = corpus_path.replace('.pdf','.txt')

    print "Building corpus from", corpus_path

    if os.path.isfile(corpus_path):
        print "Constructing toy corpus, each line is a document"
        c = toy_corpus(corpus_path, is_filename=True, nltk_stop=nltk_stop, 
                       stop_freq=stop_freq, autolabel=True)
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

    filename = get_corpus_filename(
        corpus_path, model_path, nltk_stop, stop_freq, context_type)
    c.save(filename)
    return filename 

def main(args):
    if args.model_path is None:
        if os.path.isdir(args.corpus_path):
            args.model_path = os.path.join(args.corpus_path, '../models/')
        else:
            args.model_path = os.path.dirname(args.corpus_path)
    if args.model_path and not os.path.exists(args.model_path):
        os.makedirs(args.model_path)

    args.corpus_name = os.path.basename(args.corpus_path)
    if not args.corpus_name:
        args.corpus_name = os.path.basename(os.path.dirname(args.corpus_path))

    if not args.corpus_print_name:
        args.corpus_print_name = prompt("Corpus Name", default=args.corpus_name)

    if args.htrc:
        import vsm.extensions.htrc as htrc
        htrc.proc_htrc_coll(args.corpus_path)
        
        import json
        data = [(id, htrc.metadata(id)) for id in os.listdir(args.corpus_path)
                    if os.path.isdir(id)]
        data = dict(data)
        md_filename = os.path.join(args.corpus_path, '../metadata.json')
        with open(md_filename, 'wb') as outfile:
            json.dump(data, outfile)
  
    args.corpus_filename = get_corpus_filename(
        args.corpus_path, args.model_path, stop_freq=5)
    if not args.rebuild and os.path.exists(args.corpus_filename): 
        while args.rebuild not in ['y', 'n', True]:
            args.rebuild = raw_input("\nCorpus file found. Rebuild? [y/N] ")
            args.rebuild = args.rebuild.lower().strip()
            if args.rebuild == 'y':
	        args.rebuild = True
            elif args.rebuild == '':
                args.rebuild = 'n'
    else:
        args.rebuild = True
    if args.rebuild == True:
        try:
            args.corpus_filename = build_corpus(args.corpus_path, args.model_path, 
                                                stop_freq=5)
        except IOError:
            print "ERROR: invalid path, please specify either:"
            print "  * a single plain-text file,"
            print "  * a folder of plain-text files, or"
            print "  * a folder of folders of plain-text files."
            print "\nExiting..."
            sys.exit(74)

    return write_config(args, args.config_file)


def write_config(args, config_file=None):
    """
    If config_file is None, then a name is automatically generated
    """
    config = ConfigParser()
    config.add_section("main")
    config.set("main", "path", os.path.abspath(args.model_path))
    config.set("main", "corpus_file", os.path.abspath(args.corpus_filename))
    
    config.add_section("www")
    config.set("www", "corpus_name", args.corpus_print_name)
    config.set("www", "icons", "link")
    
    config.add_section("logging")
    config.set("logging","path","logs/%s/{0}.log" % args.corpus_name)

    if args.htrc:
        config.set("main","label_module","topicexplorer.extensions.htrc")
        if not args.corpus_print_name:
            config.set("www","corpus_name","HTRC Data Capsule")
        config.set("www","doc_title_format",'<a href="{1}">{0}</a>')
        config.set("www","doc_url_format", 'http://hdl.handle.net/2027/{0}')
        config.set("www", "icons", "htrc,htrcbook,link")
        config.set("main", "htrc", True)

    if config_file is None:
        config_file = args.corpus_name + ".ini"

        overwrite = None if os.path.exists(config_file) else True
        while not overwrite:
            overwrite = raw_input("\nConfig file {0} exists. Overwrite? [Y/n] ".format(config_file))
            overwrite = overwrite.lower().strip()
            if overwrite == 'n':
                config_i = 0
                while os.path.exists(config_file):
                    config_file = args.corpus_name + ".%d.ini" % config_i
                    config_i += 1
                config_file = raw_input("Enter new filename [default: {0}]: ".format(config_file))\
                    or config_file
            elif overwrite == '' or overwrite == 'y':
                overwrite=True



    print "Writing configuration file", config_file
    with open(config_file, "wb") as configfh:
        config.write(configfh)
    return config_file

def populate_parser(parser):
    parser.add_argument("corpus_path", help="Path to Corpus",
        type=lambda x: is_valid_filepath(parser, x))
    parser.add_argument("--name", dest="corpus_print_name", 
        metavar="\"CORPUS NAME\"",
        help="Corpus name (for web interface) [Default: [corpus_path]]")
    parser.add_argument("config_file", nargs="?",
        help="Path to Config [optional]")
    parser.add_argument("--model-path", dest="model_path",
        help="Model Path [Default: [corpus_path]/../models]")
    parser.add_argument("--htrc", action="store_true")
    parser.add_argument("--rebuild", action="store_true")

if __name__ == '__main__': 
    from argparse import ArgumentParser
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()
    
    main(args)
