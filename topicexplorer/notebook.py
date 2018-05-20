from __future__ import print_function
from builtins import str
from glob import glob
import os
import os.path
import platform
import signal
import shutil
from string import Template
import sys
import time

from topicexplorer.lib.util import (overwrite_prompt, is_valid_configfile, get_static_resource_path)

if platform.system() == 'Windows':
    import topicexplorer.lib.win32


def main(args):
    args.config_file = os.path.abspath(args.config_file)
    with open(get_static_resource_path('ipynb/corpus.tmpl.py')) as corpustmpl:
        corpus_py = corpustmpl.read()
        corpus_py = Template(corpus_py)
        corpus_py = corpus_py.safe_substitute(config_file=args.config_file)

    ipynb_path = os.path.join(os.path.dirname(args.config_file), "notebooks")
    print(ipynb_path)
    if not os.path.exists(ipynb_path):
        os.makedirs(ipynb_path)

    filename = os.path.join(ipynb_path, "corpus.py")

    if overwrite_prompt(filename, default=True):
        print("Writing", filename)
        with open(filename, 'w') as corpusloader:
            corpusloader.write(corpus_py)
    pyflag = 'py2' if sys.version_info.major == 2 else 'py3'
    glob_path = (get_static_resource_path('ipynb') + '/*.{}.ipynb').format(pyflag)

    for notebook in glob(glob_path):
        new_nb_name = os.path.basename(notebook).replace('.' +pyflag, '')
        new_nb_path = os.path.join(ipynb_path, new_nb_name)
        if overwrite_prompt(new_nb_path, default=False):
            print("Copying", notebook)
            shutil.copy(notebook, new_nb_path)

    if args.launch:
        import subprocess
        os.chdir(ipynb_path)
        try:
            # TODO: Fix KeyboardInterrupt errors
            try:
                grp_fn = os.setsid
            except AttributeError:
                grp_fn = None
            proc = subprocess.Popen("jupyter notebook", shell=True, preexec_fn=grp_fn)
            # stdin=subprocess.PIPE, preexec_fn=grp_fn)
            # stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        except OSError:
            print("ERROR: Command `jupyter notebook` not found.")
            print("       If IPython or Anaconda is installed, check your PATH variable.")
            sys.exit(1)

        # CLEAN EXIT AND SHUTDOWN OF IPYTHON NOTEBOOK
        def signal_handler(signal, frame):
            # Cross-Platform Compatability
            try:
                os.killpg(proc.pid, signal)
                proc.communicate()
            except AttributeError:
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)])
                sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print("\nPress Ctrl+C to shutdown the IPython notebook server\n")

        # Cross-platform Compatability
        try:
            signal.pause()
        except AttributeError:
            # Windows hack
            while True:
                time.sleep(1)


def populate_parser(parser):
    parser.add_argument("config_file", help="Path to Config File",
                        type=lambda x: is_valid_configfile(parser, x))
    parser.add_argument('--no-launch', dest='launch', action='store_false')

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
