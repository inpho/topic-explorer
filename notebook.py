import os.path
import sys
from string import Template

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("config_file", help="Path to Config File")
args = parser.parse_args()
args.config_file = os.path.abspath(args.config_file)

with open("ipynb/corpus.tmpl.py") as corpustmpl:
    corpus_py = corpustmpl.read()
    corpus_py = Template(corpus_py)
    corpus_py = corpus_py.safe_substitute(config_file=args.config_file)

filename = os.path.basename(args.config_file).replace('.ini','')
filename = "ipynb/{0}.py".format(filename)

if os.path.exists(filename):
    overwrite = False
    while overwrite not in ['y', 'n']:
        overwrite = raw_input("\nOverwrite {0}? [y/n] ".format(filename))
        if overwrite == 'n':
            print "Exiting."
            sys.exit()

print "Writing", filename
with open(filename,'w') as corpusloader:
    corpusloader.write(corpus_py)

