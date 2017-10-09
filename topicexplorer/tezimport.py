from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import input
from builtins import range

from configparser import RawConfigParser as ConfigParser
from codecs import open
import os
import os.path
from zipfile import ZipFile

def absolutize_config_file(config_file, output_dir):
    config_file = os.path.join(output_dir, config_file)

    config = ConfigParser({'cluster': None }) 
    with open(config_file, encoding='utf8') as configfile:
        config.read_file(configfile)

    # path variables
    corpus_file = config.get('main', 'corpus_file')
    corpus_file = os.path.join(output_dir, corpus_file)
    corpus_file = os.path.abspath(corpus_file)
    config.set('main', 'corpus_file', corpus_file)

    model_pattern = config.get('main', 'model_pattern')
    model_pattern = os.path.join(output_dir, model_pattern)
    model_pattern = os.path.abspath(model_pattern)
    config.set('main', 'model_pattern', model_pattern)
    
    cluster_path = config.get('main', 'cluster')
    if cluster_path is not None and cluster_path != 'None':
        cluster_path = os.path.join(output_dir, cluster_path)
        cluster_path = os.path.abspath(cluster_path)
        config.set('main', 'cluster', cluster_path)
    
    path = config.get('main', 'path')
    if path is not None and path != 'None':
        path = os.path.join(output_dir, path)
        path = os.path.abspath(path)
        config.set('main', 'path', path)
    
    raw_corpus = config.get('main', 'raw_corpus')
    if raw_corpus is not None and raw_corpus != 'None':
        raw_corpus = os.path.join(output_dir, raw_corpus)
        raw_corpus = os.path.abspath(raw_corpus)
        config.set('main', 'raw_corpus', raw_corpus)
    
    corpus_desc = config.get('main', 'corpus_desc')
    if corpus_desc is not None and corpus_desc != 'None':
        corpus_desc = os.path.join(output_dir, corpus_desc)
        corpus_desc = os.path.abspath(corpus_desc)
        config.set('main', 'corpus_desc', corpus_desc)

    with open(config_file, 'w', encoding='utf8') as configfile:
        config.write(configfile)


def populate_parser(parser):
    parser.add_argument('tezfile', help='TEZ archive file')
    parser.add_argument('-o', '--output', default='.', required=False,
                        help="output directory")
    return parser


def main(args):
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    elif not os.path.isdir(args.output):
        raise IOError("Invalid path: must be a directory.")
    
    with ZipFile(args.tezfile) as tezfile:
        print("Extracting files...")
        tezfile.extractall(args.output)
    
    with ZipFile(args.tezfile) as tezfile:
        files = tezfile.namelist()
        config_candidates = [f for f in files if f.endswith('.ini')]
        if len(config_candidates) > 1:
            raise IOError("Multiple config files in tez archive")
        elif not config_candidates:
            raise IOError("No config file in tez archive")
        else:
            absolutize_config_file(config_candidates[0], args.output)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
