from glob import glob
import os
import os.path
import platform
import signal
import shutil
from string import Template
import sys
import time

from topicexplorer.lib.util import overwrite_prompt, is_valid_configfile

if platform.system() == 'Windows':
    import topicexplorer.lib.win32


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

    if overwrite_prompt(filename, default=True):
        print "Writing", filename
        with open(filename, 'w') as corpusloader:
            corpusloader.write(corpus_py)

    for notebook in glob(template_dir + '/*.ipynb'):
        new_nb_path = os.path.join(ipynb_path, os.path.basename(notebook))
        if overwrite_prompt(new_nb_path, default=False):
            print "Copying", notebook
            shutil.copy(notebook, ipynb_path)

    if args.launch:
        import subprocess
        import sys
        os.chdir(ipynb_path)
        try:
            # TODO: Fix KeyboardInterrupt errors
            try:
                grp_fn = os.setsid
            except AttributeError:
                grp_fn = None
            proc = subprocess.Popen("ipython notebook", shell=True, preexec_fn=grp_fn)
            # stdin=subprocess.PIPE, preexec_fn=grp_fn)
            # stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        except OSError:
            print "ERROR: Command `ipython notebook` not found."
            print "       If IPython or Anaconda is installed, check your PATH variable."
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

        print "\nPress Ctrl+C to shutdown the IPython notebook server\n"

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
