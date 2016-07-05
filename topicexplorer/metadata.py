from ConfigParser import RawConfigParser as ConfigParser

from codecs import open 
from unidecode import unidecode
from topicexplorer.lib.util import isint, is_valid_configfile, bool_prompt


def parse_metadata_from_csvfile(filename):
    """
    Takes a csvfile where the first column in each row is the label.
    Returns a dictionary of dictionaries where each key is the label,
    and each value is a dictionary of field values.
    """
    pass


def extract_metadata(corpus, filename, format='csv'):
    """
    Takes a filename to export metadata to.
    """
    pass


def extract_labels(corpus, filename):
    """
    Creates a new csv where each row is a label in the corpus.
    """


def add_metadata(corpus, ctx_type, new_metadata):
    import vsm.corpus

    label = _get_label(ctx_type)
    
    # get existing metadata
    i = corpus.context_types.index(ctx_type)
    md = corpus.context_data[i]
    fields = md.dtype.fields.keys()

    new_data = [new_metadata[id] for id in md[label]]
    new_fields = set()

    for vals in new_metadata.values():
        new_fields.add(vals.keys())

    updated_fields = new_fields.intersection(fields)
    new_fields = new_fields.difference(fields)

    for field in new_fields:
        data = [d[field] for d in new_data] #TODO: sort field by _label
        corpus = vsm.corpus.add_metadata(corpus, ctx_type, field, data)

    for field in updated_fields:
        data = [d[field] for d in new_data] #TODO: sort field by _label
        corpus.context_data[i][field] = data

    return corpus


def main(args):
    config = ConfigParser({"htrc": False,
        "sentences": "False"})
    config.read(args.config_file)
    
    args.corpus_path = config.get("main", "corpus_file")
    c = Corpus.load(args.corpus_path)

    if args.add:
        metadata = parse_metadata_from_csvfile(filename)
        c = add_metadata(c, metadata)
        c.save(args.corpus_path)


def populate_parser(parser):
    parser.add_argument("config_file", help="Path to Config",
        type=lambda x: is_valid_configfile(parser, x))
    parser.add_argument("-e", "--extract", help="Extract metadata to file")
    parser.add_argument("-a", "--add", help="Add metadata from file")
    parser.add_argument("-l", "--list")




if __name__ == '__main__':
    import argparse
    from argparse import ArgumentParser
    parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    populate_parser(parser)
    args = parser.parse_args()
    
    main(args)

