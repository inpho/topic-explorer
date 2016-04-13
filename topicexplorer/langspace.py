from codecs import open
import os
import os.path

from chardet.universaldetector import UniversalDetector
from progressbar import ProgressBar, Percentage, Bar
import topicexplorer.lib.util as util

def detect_encoding(filename):
    """
    Takes a filename and attempts to detect the character encoding of the file
    using `chardet`.
     
    :param filename: Name of the file to process
    :type filename: string

    :returns: encoding : string
    """
    detector = UniversalDetector()
    with open(filename, 'rb') as unknown_file:
        for line in unknown_file:
            detector.feed(line)
            if detector.done:
                break
    detector.close()

    return detector.result['encoding']

def convert(fname, pages=None, tokenizer='modern'):
    from topicexplorer.lib.chinese import (modern_chinese_tokenizer,
                                           ancient_chinese_tokenizer)
    import langdetect
    encoding = detect_encoding(fname)
    with open(fname, encoding=encoding) as infile:
        data = infile.read()
    lang = langdetect.detect(data)

    if tokenizer == 'modern':
        tokenizer = modern_chinese_tokenizer
    elif tokenizer == 'ancient':
        tokenizer = ancient_chinese_tokenizer

    if lang.startswith('zh'):
        # add space before each non-ascii character
        #data = u' '.join(list(mmseg.search.seg_txt_search(data)))
        #data = u''.join(ltr if ord(ltr) < 128 
        #                    else u' ' + ltr + u' ' for ltr in data)
        data = u' '.join(tokenizer(data))

    return data


def convert_and_write(fname, output_dir=None, overwrite=False, verbose=False,
    tokenizer='modern'):

    output = os.path.basename(fname) 
    if output_dir:
        output = os.path.join(output_dir, output)
    if output_dir is not None and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if overwrite or util.overwrite_prompt(output):
        with open(output, 'wb', encoding='utf8') as outfile:
            outfile.write(convert(fname, tokenizer=tokenizer))
            if verbose:
                print "converted", fname, "->", output

def main(args, verbose=1):
    path_or_paths = args.path
    output_dir = args.output
    if isinstance(path_or_paths, basestring):
        path_or_paths = [path_or_paths]

    for p in path_or_paths:
        if os.path.isdir(p):
            num_files = len(list(util.find_files(p, '*')))
            if verbose == 1:
                pbar = ProgressBar(widgets=[Percentage(), Bar()],
                                   maxval=num_files).start()
            for file_n, pdffile in enumerate(util.find_files(p, '*')):
                convert_and_write(pdffile, output_dir, overwrite=True)
                if verbose == 1:
                    pbar.update(file_n)

            if verbose == 1:
                pbar.finish()
        else:
            convert_and_write(p, output_dir, overwrite=True, verbose=True)

def populate_parser(parser):
    parser.add_argument("path", nargs='+', help="file or folder to parse",
        type=lambda x: util.is_valid_filepath(parser, x))
    parser.add_argument("--tokenizer", choices=['ancient', 'modern'], default="modern")
    parser.add_argument("-o", '--output', required=True,
        help="output path")

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
