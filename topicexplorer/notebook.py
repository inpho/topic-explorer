from glob import glob
import os, os.path
import shutil
import sys
from string import Template

def main(args):
    args.config_file = os.path.abspath(args.config_file)
    
    with open("ipynb/corpus.tmpl.py") as corpustmpl:
        corpus_py = corpustmpl.read()
        corpus_py = Template(corpus_py)
        corpus_py = corpus_py.safe_substitute(config_file=args.config_file)
    
    ipynb_path = os.path.join(os.path.dirname(args.config_file), "notebooks")
    print ipynb_path
    if not os.path.exists(ipynb_path):
        os.makedirs(ipynb_path)

    filename = os.path.join(ipynb_path, "corpus.py")
    
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

    for notebook in glob('ipynb/*.ipynb'):
        print "Copying", notebook
        shutil.copy(notebook, ipynb_path)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("config_file", help="Path to Config File")
    args = parser.parse_args()
