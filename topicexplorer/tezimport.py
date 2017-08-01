from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import input
from builtins import range

import os
import os.path
from zipfile import ZipFile

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

if __name__ == '__main__':
    main()
