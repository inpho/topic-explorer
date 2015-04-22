from glob import glob
import os, os.path
import shutil
import sys
from string import Template

def main(args):
    args.config_file = os.path.abspath(args.config_file)
   
    template_dir = os.path.dirname(__file__)
    template_dir = os.path.join(template_dir, '../ipynb/')
    template_dir = os.path.normpath(template_dir)
    with open(os.path.join(template_dir, 'corpus.tmpl.py')) as corpustmpl:
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

    for notebook in glob(os.path.join(template_dir, '*.ipynb')):
        print "Copying", notebook
        shutil.copy(notebook, ipynb_path)

    if args.launch:
        import subprocess, sys
        os.chdir(ipynb_path)
        try:
            # TODO: Fix KeyboardInterrupt errors
            subprocess.call(["ipython","notebook"])
        except OSError:
            print "ERROR: Command `ipython notebook` not found."
            print "       If IPython or Anaconda is installed, check your PATH variable."
            sys.exit(1)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("config_file", help="Path to Config File")
    args = parser.parse_args()
