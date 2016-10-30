from ConfigParser import RawConfigParser as ConfigParser
from collections import defaultdict
import os
import os.path
import shutil
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from topicexplorer.lib.util import (prompt, is_valid_filepath, bool_prompt,
                                    listdir_nohidden, contains_pattern)


def get_corpus_filename(corpus_path, model_path, nltk_stop=False, stop_freq=0,
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


def process_pdfs(corpus_path, ignore=['.json', '.log', '.err', '.pickle', '.npz']):
    from topicexplorer.lib import pdf
    if os.path.isfile(corpus_path):
        print "PDF file detected, extracting plaintext to",\
            corpus_path.replace('.pdf', '.txt')
        pdf.main(corpus_path)
        corpus_path = corpus_path.replace('.pdf', '.txt')
    elif os.path.isdir(corpus_path):
        print "PDF files detected, extracting plaintext to", corpus_path + '-txt'

        if corpus_path.endswith('/'):
            corpus_path = corpus_path[:-1]

        # TODO: Add processing of collections
        contents = listdir_nohidden(corpus_path)
        contents = [os.path.join(corpus_path, obj) for obj in contents
                    if not any([obj.endswith(suffix) for suffix in ignore])]
        count_dirs = len(filter(os.path.isdir, contents))
        count_files = len(filter(os.path.isfile, contents))

        if count_files > 0 and count_dirs == 0:
            # process all files
            pdf.main(corpus_path, corpus_path + '-txt')
        elif count_dirs > 0 and count_files == 0:
            # process each subdirectory
            for directory in contents:
                pdf.main(directory,
                         directory.replace(corpus_path, corpus_path + '-txt'))
        else:
            raise IOError("Invalid Path: empty directory")

        corpus_path += '-txt'
    return corpus_path


def process_bibtex(corpus_path):
    import pybtex
    from pybtex.database import parse_file
    from topicexplorer.lib.util import overwrite_prompt, safe_symlink

    print "Loading BibTeX from", corpus_path
    bib = parse_file(corpus_path)

    target_dir = os.path.basename(corpus_path).replace('.bib', '')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    elif overwrite_prompt(target_dir) and not args.quiet:
        shutil.rmtree(target_dir)
        os.makedirs(target_dir)
    else:
        raise IOError("Path exits: {}".format(target_dir))

    for entry in bib.entries:
        if bib.entries[entry].fields.get('file', None):
            filename = '/' + bib.entries[entry].fields['file'].replace(':pdf', '')[1:]
            if 'C$\\backslash$:' in filename:
                filename = filename.replace('C$\\backslash$:', '')
                filename = filename[1:]
                filename = os.path.normpath(filename)
            filename = os.path.abspath(filename)
            if not os.path.exists(filename):
                print "Invalid 'file' field for BibTeX entry {}:\n\t({})".format(entry, filename)
            else:
                new_path = os.path.join(target_dir, os.path.basename(filename))
                try:
                    safe_symlink(filename, new_path)
                except OSError:
                    print "Error linking file for BibTeX entry {}:\n\t({})".format(entry, filename)
        else:
            print "No 'file' field for BibTeX entry: {}".format(entry)

    return target_dir


def get_corpusbuilder_fn(corpus_path, sentences=False, ignore=[]):
    relpaths = [os.path.relpath(path, start=corpus_path)
                for path in listdir_nohidden(corpus_path, recursive=True)
                if os.path.isfile(path)
                and not any([path.endswith(i) for i in ignore])]

    dir_counts = defaultdict(int)
    for path in relpaths:
        dir_counts[os.path.dirname(path)] += 1

    dirs = dir_counts.keys()
    populated_levels = [dir.count(os.path.sep)
                        for dir, key in dir_counts.iteritems()]

    levels = max(populated_levels) - min(populated_levels)
    print "{} files, {} dirs, {} levels".format(len(relpaths), len(dirs), levels)

    if len(relpaths) == 1:
        if sentences:
            from vsm.extensions.ldasentences import toy_corpus
        else:
            from vsm.extensions.corpusbuilders import toy_corpus
        import functools
        return functools.partial(toy_corpus, is_filename=True, autolabel=True)
    elif len(dirs) <= 1:
        if sentences:
            from vsm.extensions.ldasentences import dir_corpus
        else:
            from vsm.extensions.corpusbuilders import dir_corpus
        return dir_corpus
    elif sentences:
        raise NotImplementedError("""Collection corpuses are too large for
        sentence parsing. Reduce your corpus to a single folder or
        file.""")
    elif levels == 0 and max(populated_levels) == 1:
        from vsm.extensions.corpusbuilders import coll_corpus
        return coll_corpus
    else:
        from vsm.extensions.corpusbuilders import walk_corpus
        return walk_corpus


def build_corpus(corpus_path, model_path, nltk_stop=False, stop_freq=0,
                 context_type='document', ignore=['.json', '.log', '.err', '.pickle', '.npz'],
                 decode=True, sentences=False, simple=True, tokenizer='default'):

    from vsm.corpus import Corpus

    # import appropriate tokenizer
    if tokenizer == 'default':
        from vsm.extensions.corpusbuilders.util import word_tokenize
        tokenizer = word_tokenize
    elif tokenizer == 'zh':
        from topicexplorer.lib.chinese import modern_chinese_tokenizer
        tokenizer = modern_chinese_tokenizer
    elif tokenizer == 'ltc' or tokenizer == 'och':
        from topicexplorer.lib.chinese import ancient_chinese_tokenizer
        tokenizer = ancient_chinese_tokenizer
    elif tokenizer == 'inpho':
        from topicexplorer.extensions.inpho import inpho_tokenizer
        tokenizer = inpho_tokenizer
    elif tokenizer == 'brain':
        from hyperbrain.parse import brain_tokenizer
        tokenizer = brain_tokenizer
    else:
        raise NotImplementedError(
            "Tokenizer '{}' is not included in topicexplorer".format(tokenizer))

    # pre-process PDF files
    contains_pdfs = corpus_path[-4:] == '.pdf' or contains_pattern(corpus_path, '*.pdf')
    if contains_pdfs:
        corpus_path = process_pdfs(corpus_path)

    print "Building corpus from", corpus_path,
    corpusbuilder = get_corpusbuilder_fn(corpus_path, sentences, ignore=ignore)
    print "with {} function".format(corpusbuilder.__name__)

    c = corpusbuilder(corpus_path, nltk_stop=nltk_stop,
                      stop_freq=stop_freq, ignore=ignore, decode=decode,
                      simple=simple, tokenizer=tokenizer)

    if contains_pdfs:
        from vsm.viewer.wrappers import doc_label_name
        import re
        label_name = doc_label_name(c.context_types[0])
        new_labels = [re.sub('txt$', 'pdf', label) for label in c.context_data[0][label_name]]
        c.context_data[0][label_name] = new_labels

    filename = get_corpus_filename(
        corpus_path, model_path, nltk_stop, stop_freq, context_type)
    c.save(filename)
    return filename


def main(args):
    # convert to unicode to avoid windows errors
    args.corpus_path = unicode(args.corpus_path, 'utf-8')

    # config corpus_path
    # process bibtex files
    args.bibtex = args.corpus_path.endswith('.bib')
    if args.bibtex:
        args.bibtex = args.corpus_path
        args.corpus_path = process_bibtex(args.corpus_path)

    # set corpus_name
    args.corpus_name = os.path.basename(args.corpus_path)
    if not args.corpus_name:
        args.corpus_name = os.path.basename(os.path.dirname(args.corpus_path))

    if not args.corpus_print_name and not args.quiet:
        args.corpus_print_name = prompt("Corpus Name", default=args.corpus_name)

    if args.htrc:
        import vsm.extensions.htrc as htrc
        htrc.proc_htrc_coll(args.corpus_path)

        import json
        data = [(id, htrc.metadata(id)) for id in listdir_nohidden(args.corpus_path)
                if os.path.isdir(id)]
        data = dict(data)
        md_filename = os.path.join(args.corpus_path, '../metadata.json')
        with open(md_filename, 'wb') as outfile:
            json.dump(data, outfile)

    # configure model-path
    if args.model_path is None:
        if os.path.isdir(args.corpus_path):
            args.model_path = os.path.join(args.corpus_path, '../models/')
        else:
            args.model_path = os.path.dirname(args.corpus_path)
    if args.model_path and not os.path.exists(args.model_path):
        os.makedirs(args.model_path)

    args.corpus_filename = get_corpus_filename(
        args.corpus_path, args.model_path, stop_freq=args.stop_freq)
    if not args.rebuild and os.path.exists(args.corpus_filename):
        args.rebuild = bool_prompt("\nCorpus file found. Rebuild? ", 
            default=False)
    else:
        args.rebuild = True
    if args.rebuild:
        try:
            args.corpus_filename = build_corpus(args.corpus_path, args.model_path,
                                                stop_freq=args.stop_freq, decode=args.decode,
                                                sentences=args.sentences,
                                                simple=args.simple, tokenizer=args.tokenizer)
        except IOError:
            print "ERROR: invalid path, please specify either:"
            print "  * a single plain-text or PDF file,"
            print "  * a single bibtex (.bib) file with 'file' fields,"
            print "  * a folder of plain-text or PDF files, or"
            print "  * a folder of folders of plain-text or PDF files."
            print "\nExiting..."
            sys.exit(74)
        """
        except LookupError as e:
            if 'punkt' in e.message:
                print "\nERROR: sentence tokenizer not available, download by running:"
                print "    python -m nltk.downloader punkt"

            elif 'stopwords' in e.message:
                print "\nERROR: stopwords not available, download by running:"
                print "    python -m nltk.downloader stopwords"
            else:
                raise e
            print "\nExiting..."
            sys.exit(74)
        """

    args.config_file = write_config(args, args.config_file)

    args.corpus_desc = args.config_file + '.md'
    if not args.quiet and os.path.exists(args.corpus_desc):
        while args.corpus_desc not in ['y', 'n', False]:
            args.corpus_desc = raw_input("\nExisting corpus description found. Remove? [y/N] ")
            args.corpus_desc = args.corpus_desc.lower().strip()
            if args.corpus_desc == '':
                args.corpus_desc = False
        else:
            if args.corpus_desc == 'y':
                args.corpus_desc = args.config_file + '.md'

    if args.corpus_desc:
        with open(args.corpus_desc, 'w') as outfile:
            outfile.write(
"""This is an instance of the [InPhO Topic Explorer](http://inphodata.cogs.indiana.edu/). If you would like
to add a custom corpus description, either:
- Modify the contents of the file `{}`
- Change the main:corpus_desc path in `{}` to an existing Markdown file.
""".format(os.path.abspath(args.corpus_desc), 
           os.path.abspath(args.config_file)))

    return args.config_file



def write_config(args, config_file=None):
    """
    If config_file is None, then a name is automatically generated
    """
    config = ConfigParser()
    config.add_section("main")
    config.set("main", "path", os.path.abspath(args.model_path))
    config.set("main", "corpus_file", os.path.abspath(args.corpus_filename))
    config.set("main", "raw_corpus", os.path.abspath(args.corpus_path))
    config.set("main", "sentences", args.sentences)

    if args.bibtex:
        config.set("main", "label_module", "topicexplorer.extensions.bibtex")
        config.add_section("bibtex")
        config.set("bibtex", "path", args.bibtex)

    config.add_section("www")
    config.set("www", "corpus_name", args.corpus_print_name)
    config.set("www", "icons", "link")
    config.set("www", "fulltext", "false")


    config.add_section("logging")
    config.set("logging", "path", "logs/%s/{0}.log" % args.corpus_name)

    if args.htrc:
        config.set("main", "label_module", "topicexplorer.extensions.htrc")
        if not args.corpus_print_name:
            config.set("www", "corpus_name", "HTRC Data Capsule")
        config.set("www", "doc_title_format", '<a href="{1}">{0}</a>')
        config.set("www", "doc_url_format", 'http://hdl.handle.net/2027/{0}')
        config.set("www", "icons", "htrc,htrcbook,link")
        config.set("main", "htrc", True)

    if args.tokenizer in ['zh','ltc','och']:
        config.set("main", "lang", "cn")

    if config_file is None:
        config_file = args.corpus_name + ".ini"

        if os.path.basename(args.corpus_path) == args.corpus_name:
            config_file = os.path.join(args.corpus_path, '..', config_file)
            config_file = os.path.normpath(config_file)

        overwrite = None if os.path.exists(config_file) and not args.quiet else True
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
                overwrite = True

    config.set("main", "corpus_desc", config_file+'.md')

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

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unicode", action="store_false", dest='decode',
                       help="Store unicode characters. [Default]")
    group.add_argument("--decode", action="store_true", dest='decode',
                       help="Convert unicode characters to ascii.")
    parser.set_defaults(decode=False)

    parser.add_argument("--htrc", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--tokenizer", default="default",
        choices=['zh', 'ltc', 'och', 'inpho', 'default', 'brain'])

    parser.add_argument("--simple", action="store_true", default=True,
                        help="Skip sentence tokenizations [default].")
    parser.add_argument("--sentences", action="store_true", help="Parse at the sentence level")
    parser.add_argument("--freq", dest="stop_freq", default=5, type=int,
                        help="Filter words occurring less than freq times [Default: 5])")


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
