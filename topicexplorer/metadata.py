from ConfigParser import RawConfigParser as ConfigParser

from codecs import open 
from unidecode import unidecode
from topicexplorer.lib.util import isint, is_valid_configfile, bool_prompt


def parse_metadata_from_file(filename):
    """
    Takes a csvfile where the first column in each row is the item id.
    """
    pass


def main(args):
    pass


def populate_parser(parser):
    parser.add_argument("config_file", help="Path to Config",
        type=lambda x: is_valid_configfile(parser, x))


if __name__ == '__main__':
    import argparse
    from argparse import ArgumentParser
    parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    populate_parser(parser)
    args = parser.parse_args()
    
    main(args)

