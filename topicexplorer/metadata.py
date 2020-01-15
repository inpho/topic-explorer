"""
Assists with metadata management.

The ``topicexplorer metadata`` command provides several metadata management
tools. It works with tab-separated files (TSV).

Example Workflow
------------------

A typical workflow, assuming a Topic Explorer environment defined by
``example.ini``:

1.  Extract metadata with ``topicexplorer metadata -e metadata.tsv example.ini``
2.  Open file in a text editor to change values.
3.  Save file.
4.  Update metadata with ``topicexplorer metadata -a metadata.tsv example.ini``

For label updating, see documentation for |list labels|_.

.. |list labels| replace:: 
    list labels (``-l``)

.. _list labels:
    #list-labels-l


Command Line Arguments
------------------------

Extract Metadata (``-e``)
'''''''''''''''''''''''''''
Extracts all metadata to a TSV file.


List labels (``-l``)
''''''''''''''''''''''
Extracts labels to a TSV file.

Usage should be combined with ``--rename``:

1.  ``topicexplorer metadata -l labels.tsv example.ini``
2.  Edit the labels you wish to change.
3.  ``topicexplorer metadata --rename -a labels.tsv example.ini``


Force insertion (``-f``)
''''''''''''''''''''''''''
Forces blank metadata to be inserted for non-specified fields.


Rename labels (``--rename``)
''''''''''''''''''''''''''''''
Changing document labels can cause many issues for reconstructing the document,
any renames must be explicitly enabled with the ``--rename`` flag. Documents
will be updated assuming the original order of the extracted TSV file.


HathiTrust Integration (``--htrc``)
'''''''''''''''''''''''''''''''''''''
The ``topicexplorer metadata --htrc`` command will add volume titles and 
links to the HathiTrust Page Turner fulltext view to the InPhO Topic Explorer
document view.

The argument is only a flag, and does not require a TSV file to be specified.

.. seealso::
    `HathiTrust Integrations`_
        Expanded documentation of the HathiTrust integrations.

.. _HathiTrust Integrations: htrc.html


"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str

from ast import literal_eval
from codecs import open 
import csv
import os.path

import topicexplorer.config
from topicexplorer.lib.util import isint, is_valid_configfile, bool_prompt
from sortedcontainers import SortedDict
from unidecode import unidecode

from vsm import Corpus
from vsm.viewer.wrappers import doc_label_name

def parse_value(value):
    try:
        return literal_eval(value)
    except (ValueError, SyntaxError):
        return value

def UnicodeDictReader(utf8_data, **kwargs):
    # Solution from http://stackoverflow.com/a/5005573
    # added literal_eval to convert to native types.
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: parse_value(value)
                    for key, value in row.items()}

def parse_metadata_from_csvfile(filename, context_type):
    """
    Takes a csvfile where the first column in each row is the label.
    Returns a dictionary of dictionaries where each key is the label,
    and each value is a dictionary of field values.
    """
    label_name = doc_label_name(context_type)

    with open(filename, encoding='utf8') as csvfile:
        reader = UnicodeDictReader(csvfile, delimiter='\t',
                                   quoting=csv.QUOTE_NONE)
        metadata = SortedDict()
        for row in reader:
            metadata[row[label_name]] = row

    return metadata

def extract_metadata(corpus, ctx_type, filename, format='tsv'):
    """
    Takes a corpus object, a context_type, and a filename to export
    all metadata to.
    """
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
        ctx_index = corpus.context_types.index(ctx_type)

        ctx_data = corpus.context_data[ctx_index]
        writer.writerow(ctx_data.dtype.names)
        for row in ctx_data:
            writer.writerow(row)


def extract_labels(corpus, ctx_type, filename):
    """
    Creates a new csv where each row is a label in the corpus.
    """
    label_name = doc_label_name(ctx_type)
    labels = corpus.view_metadata(ctx_type)[label_name]

    with open(filename, 'w') as outfile:
        outfile.write(label_name + '\n')
        for label in labels:
            outfile.write(label + '\n')


def add_metadata(corpus, ctx_type, new_metadata, force=False, rename=False):
    import vsm.corpus
    
    # get existing metadata
    i = corpus.context_types.index(ctx_type)
    md = corpus.context_data[i]
    fields = md.dtype.fields.keys()

    # sort new_metadata according to existing md order
    # Note: this may raise a KeyError - in which case there's not md
    # for each entry.
    label_name = doc_label_name(ctx_type)
    labels = md[label_name]
    if rename:
        new_data = new_metadata.values()
    else:
        try:
            if force:
                new_data = [new_metadata.get(id, {}) for id in labels]
            else:
                new_data = [new_metadata[id] for id in labels]

            if not new_data:
                print("No metadata labels match existing labels.")
                print("If you changed labels, run with the `--rename` flag.")
                sys.exit(0)
            elif not force and len(new_data) != len(labels):
                raise KeyError
        except KeyError:
            print("New metadata does not span all documents in corpus.")
            print("If you changed labels, run with the `--rename` flag.")
            print("If you wish to force insertion of blank metadata,")
            print("run with the `--force` flag.")
            import sys
            sys.exit(1)

    # look for new fields
    new_fields = set()
    for vals in new_metadata.values():
        new_fields.update(vals.keys())

    # differentiate new and updated fields
    updated_fields = new_fields.intersection(fields)
    if not rename:
        updated_fields.remove(label_name)
    new_fields = new_fields.difference(fields)
    if None in new_fields:
        new_fields.remove(None)

    # process new fields
    for field in new_fields:
        if force:
            data = [d.get(field, '') for d in new_data]
        else:
            # new_data is a sorted list of metadata dictionaries
            data = [d[field] for d in new_data]
        corpus = vsm.corpus.add_metadata(corpus, ctx_type, field, data)

    # process existing fields
    for field in updated_fields:
        if force:
            data = [d.get(field, '') for d in new_data]
        else:
            data = [d[field] for d in new_data]
        corpus.context_data[i][field] = data

    return corpus


def add_htrc_metadata(config, corpus=None, corpus_filename=None):
    import htrc.metadata

    config.set("main", "label_module", "topicexplorer.extensions.htrc")
    config.set("www", "doc_title_format", '<a href="{1}">{0}</a>')
    config.set("www", "doc_url_format", 'http://hdl.handle.net/2027/{0}')
    config.set("www", "icons", "htrcbook,link")
    config.set("main", "htrc", "True")
    
    if corpus_filename:
        corpus = Corpus.load(corpus_filename)
        config.set("main", "context_type", corpus.context_types[0])
    
    if corpus:
        ctx_type = config.get("main", "context_type")
        label_name = doc_label_name(ctx_type)
        ids = corpus.view_metadata(ctx_type)[label_name]
        
        htrc_metapath = os.path.abspath(config.get("main", "corpus_file"))
        htrc_metapath = os.path.join(
            os.path.dirname(htrc_metapath),
            os.path.basename(htrc_metapath) + '.metadata.json')

        print("Downloading metadata to ", htrc_metapath)
        htrc.metadata.get_metadata(ids, output_file=htrc_metapath)
        
        config.set("www", "htrc_metadata", htrc_metapath)

    return config

def main(args):
    from vsm.corpus import Corpus

    config = topicexplorer.config.read(args.config_file)
    
    args.corpus_path = config.get("main", "corpus_file")
    c = Corpus.load(args.corpus_path)
    
    context_type = config.get('main', 'context_type')

    if args.add:
        metadata = parse_metadata_from_csvfile(args.add, context_type)
        c = add_metadata(c, context_type, metadata, force=args.force,
            rename=args.rename)
        c.save(args.corpus_path)
    if args.list:
        extract_labels(c, context_type, args.list)
    if args.extract:
        extract_metadata(c, context_type, args.extract)
    if args.htrc:
        config = add_htrc_metadata(config, corpus=c)
        with open(args.config_file, "w") as configfh:
            config.write(configfh)


def populate_parser(parser):
    parser.add_argument("config_file", help="Path to Config",
        type=lambda x: is_valid_configfile(parser, x))
    parser.add_argument("-e", "--extract", help="Extract metadata to file")
    parser.add_argument("-a", "--add", help="Add metadata from file")
    parser.add_argument("-l", "--list", help="List all labels")
    parser.add_argument("--rename", action='store_true', default=False,
        help="Rename labels, assumes same document order. See documentation.")
    parser.add_argument("-f", "--force", action='store_true', default=False,
        help="Force insertion of blank metadata")
    parser.add_argument("--htrc", action='store_true', default=False,
        help="Download HTRC metadata and configure explorer.")


if __name__ == '__main__':
    import argparse
    from argparse import ArgumentParser
    parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    populate_parser(parser)
    args = parser.parse_args()
    
    main(args)

