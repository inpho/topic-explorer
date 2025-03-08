from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import input
from builtins import range

import ast
from codecs import open
import os
import os.path
import sys
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import topicexplorer.config
from topicexplorer.lib.util import is_valid_configfile

def build_manifest(config_file, corpus_file, model_pattern, topic_range,
                   cluster_path=None, raw_corpus=None, corpus_desc=None,
                   htrc_metapath=None):
    files = [config_file, corpus_file]

    for k in topic_range:
        files.append(model_pattern.format(k))

    if cluster_path and cluster_path != 'None':
        files.append(cluster_path)
    if corpus_desc and corpus_desc != 'None':
        files.append(corpus_desc)

    if htrc_metapath and htrc_metapath != 'None':
        files.append(htrc_metapath)

    if raw_corpus and raw_corpus != 'None':
        for root, dirs, corpus_files in os.walk(raw_corpus):
            for f in corpus_files:
                files.append(os.path.join(root, f))

    return files

def create_relative_config_file(config_file, manifest, include_corpus=False):
    if sys.version_info[0] == 3:
        root = os.path.commonpath(map(os.path.abspath, manifest)) + '/'
    else:
        root = os.path.commonprefix(map(os.path.abspath, manifest))
    
    config = topicexplorer.config.read(config_file)

    # path variables
    corpus_file = config.get('main', 'corpus_file')
    model_pattern = config.get('main', 'model_pattern')
    cluster_path = config.get('main', 'cluster')
    path = config.get('main', 'path')
    raw_corpus = config.get('main', 'raw_corpus')
    corpus_desc = config.get('main', 'corpus_desc')
    
    config.set('main', 'corpus_file', corpus_file.replace(root, ''))
    config.set('main', 'model_pattern', model_pattern.replace(root, ''))
    if cluster_path is not None:
        config.set('main', 'cluster', cluster_path.replace(root, ''))
    if path is not None:
        config.set('main', 'path', path.replace(root, ''))
    if raw_corpus is not None and include_corpus:
        config.set('main', 'raw_corpus', raw_corpus.replace(root, ''))
    else:
        config.set('main', 'raw_corpus', None)
    if corpus_desc is not None:
        config.set('main', 'corpus_desc', corpus_desc.replace(root, ''))
    try:
        if config.getboolean('main', 'htrc'):
            htrc_metapath = config.get('www', 'htrc_metadata')
            if htrc_metapath is not None:
                config.set('www', 'htrc_metadata', htrc_metapath.replace(root, ''))
    except:
        pass

    tempfh = NamedTemporaryFile(prefix='tez.'+config_file, delete=False)
    temp_config_file = tempfh.name
    tempfh.close()
    with open(temp_config_file, 'w', encoding='utf-8') as tempfile:
        config.write(tempfile)

    return temp_config_file

def zip_files(outfile, manifest, include_corpus=False, verbose=False):
    if sys.version_info[0] == 3:
        root = os.path.commonpath(map(os.path.abspath, manifest))
    else:
        root = os.path.commonprefix(map(os.path.abspath, manifest))

    files = [(f, os.path.relpath(f, root)) for f in manifest]

    # relativize the config
    tempfile = create_relative_config_file(
        files[0][0], manifest, include_corpus)
    files[0] = (tempfile, files[0][1])

    with ZipFile(outfile, 'w') as output:
        print("Constructing archive {}".format(outfile))
        for path, arcpath in files:
            if verbose:
                print("Exporting {}".format(arcpath))
            output.write(path, arcpath)

    os.remove(tempfile)

def populate_parser(parser):
    parser.add_argument('config', type=lambda x: is_valid_configfile(parser, x),
                        help="Configuration file path")
    parser.add_argument('-o', '--output', help="Output path for arcive (.tez)",
                        required=False, default=None)
    parser.add_argument('--include-corpus', help="Include raw corpus files",
                        action='store_true', dest='include_corpus')
    return parser


def main(args=None):
    #open config for reading
    config = topicexplorer.config.read(args.config)

    # clean up output file path
    if args.output is None:
        args.output = args.config.replace('.ini', '.tez') 
    if not args.output.endswith('.tez'):
        args.output += '.tez'

    # path variables
    context_type = config.get('main', 'context_type')
    corpus_file = config.get('main', 'corpus_file')
    model_pattern = config.get('main', 'model_pattern')
    cluster_path = config.get('main', 'cluster')
    corpus_desc = config.get('main', 'corpus_desc')
    
    # topic variables
    if config.get('main', 'topics'):
        topic_range = ast.literal_eval(config.get('main', 'topics'))
    if args.include_corpus:
        raw_corpus = config.get('main', 'raw_corpus')
    else:
        raw_corpus = None

    try:
        if config.getboolean('main', 'htrc'):
            htrc_metapath = config.get('www', 'htrc_metadata')
        else:
            htrc_metapath = None
    except:
        htrc_metapath = None

    # get manifest for zip file
    filenames = build_manifest(
        args.config, corpus_file, model_pattern, topic_range, cluster_path,
        raw_corpus=raw_corpus, corpus_desc=corpus_desc,
        htrc_metapath=htrc_metapath)

    zip_files(args.output, filenames, args.include_corpus)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
