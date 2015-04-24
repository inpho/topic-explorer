#!/usr/bin/env python
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import PDFException
from pdfminer.psparser import PSException

import os.path
from glob import glob
from codecs import open

from topicexplorer.lib import util

from progressbar import ProgressBar, Percentage, Bar

def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    text += '\n'
    return text 

def convert_and_write(fname, output_dir=None, overwrite=False, verbose=False):
    output = os.path.basename(fname) 
    output = output.replace('.pdf','.txt')
    if output_dir:
        output = os.path.join(output_dir, output)
    if output_dir is not None and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if overwrite or util.overwrite_prompt(output):
        with open(output, 'wb') as outfile:
            outfile.write(convert(fname))
            if verbose:
                print "converted", fname, "->", output

def main(path_or_paths, output_dir=None, verbose=1):
    if isinstance(path_or_paths, basestring):
        path_or_paths = [path_or_paths]

    for p in path_or_paths:
        if os.path.isdir(p):
            num_files = len(list(util.find_files(p, '*.pdf')))
            if verbose == 1:
                pbar = ProgressBar(widgets=[Percentage(), Bar()],
                                   maxval=num_files).start()
            for file_n, pdffile in enumerate(util.find_files(p, '*.pdf')):
                try:
                    convert_and_write(pdffile, output_dir, overwrite=True)
                except (PDFException, PSException):
                    print "Skipping {0} due to PDF Exception".format(pdffile)

                if verbose == 1:
                    pbar.update(file_n)

            if verbose == 1:
                pbar.finish()
        else:
            convert_and_write(p, output_dir, overwrite=True, verbose=True)

    

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("path", nargs='+', help="PDF file or folder to parse",
        type=lambda x: util.is_valid_filepath(parser, x))
    parser.add_argument("-o", '--output',
        help="output path [default: same as filename]")

    args = parser.parse_args()

    main(args.path, args.output)
