#!/usr/bin/env python
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from past.builtins import basestring

from codecs import open
import concurrent.futures
from glob import glob
from io import BytesIO
import os
import os.path
import platform
import subprocess

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import PDFException
from pdfminer.psparser import PSException
from progressbar import ProgressBar, Percentage, Bar

from topicexplorer.lib import util

try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote

def convert(fname, pages=None):
    try:
        # attempt to find a pdftotext binary
        cmd = "where" if platform.system() == "Windows" else "which"
        cmd = subprocess.check_output(cmd + ' pdftotext', shell=True)
        cmd = cmd.decode('utf8').strip()
        if not cmd:
            raise EnvironmentError("pdftotext not found")
        
        return subprocess.check_output(' '.join([cmd, cmd_quote(fname), '-']), shell=True)
    except (EnvironmentError, subprocess.CalledProcessError):
        #logging.warning("pdftotext not found, defaulting to pdfminer.")
        return convert_miner(fname, pages=pages)

def convert_miner(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = BytesIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, codec='utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    text = output.getvalue()
    infile.close()
    converter.close()
    output.close()
    text += '\n'.encode('utf-8')
    return text


def convert_and_write(fname, output_dir=None, overwrite=False, verbose=False):
    output = os.path.basename(fname)
    output = output.replace('.pdf', '.txt')
    if output_dir:
        output = os.path.join(output_dir, output)
    if output_dir is not None and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if overwrite or util.overwrite_prompt(output):
        with open(output, 'wb') as outfile:
            outfile.write(convert(fname))
            if verbose:
            	print("converted", fname, "->", output)


def main(path_or_paths, output_dir=None, verbose=1):
    if isinstance(path_or_paths, basestring):
        path_or_paths = [path_or_paths]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for p in path_or_paths:
            if os.path.isdir(p):
                for file_n, pdffile in enumerate(util.find_files(p, '*.pdf')):
                    try:
                        futures.append(executor.submit(
                            convert_and_write, pdffile, output_dir, True))
                    except (PDFException, PSException):
                        print("Skipping {0} due to PDF Exception".format(pdffile))
            else:
                pdffile = p
                futures.append(executor.submit(convert_and_write, pdffile, output_dir, True, True))

        if verbose == 1:
            pbar = ProgressBar(widgets=[Percentage(), Bar()],
                               maxval=len(futures)).start()

            for file_n, f in enumerate(concurrent.futures.as_completed(futures)):
                pbar.update(file_n)

            pbar.finish()

"""
# This drop in replacement is for testing of the pdf converters in serial
def main(path_or_paths, output_dir=None, verbose=1):
    if isinstance(path_or_paths, basestring):
        path_or_paths = [path_or_paths]

    pbar = ProgressBar(widgets=[Percentage(), Bar()]).start()
    for p in pbar(path_or_paths):
        if os.path.isdir(p):
            for file_n, pdffile in enumerate(util.find_files(p, '*.pdf')):
                try:
                    convert_and_write(pdffile, output_dir, True)
                except (PDFException, PSException):
                    print("Skipping {0} due to PDF Exception".format(pdffile))
        else:
            pdffile = p
            convert_and_write(pdffile, output_dir, True, True)


    pbar.finish()
"""


if __name__ == '__main__':  # pragma: no cover
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("path", nargs='+', help="PDF file or folder to parse",
                        type=lambda x: util.is_valid_filepath(parser, x))
    parser.add_argument("-o", '--output',
                        help="output path [default: same as filename]")

    args = parser.parse_args()

    main(args.path, args.output)
