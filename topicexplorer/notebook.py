from glob import glob
import os, os.path
import signal
import shutil
import sys
import time
from string import Template

def overwrite_prompt(filename):
    if os.path.exists(filename):
        overwrite = False
        while overwrite not in ['y', 'n', True]:
            overwrite = raw_input("\nOverwrite {0}? [Y/n] ".format(filename))
            overwrite = overwrite.lower().strip()
            if overwrite == 'y' or overwrite == '':
                return True
        return False
    else:
        return True

    

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

    if overwrite_prompt(filename):
        print "Writing", filename
        with open(filename,'w') as corpusloader:
            corpusloader.write(corpus_py)

    for notebook in glob(os.path.join(template_dir, '*.ipynb')):
        new_nb_path = os.path.join(ipynb_path, os.path.basename(notebook))
        if overwrite_prompt(new_nb_path):
            print "Copying", notebook
            shutil.copy(notebook, ipynb_path)

    if args.launch:
        import subprocess, sys
        os.chdir(ipynb_path)
        try:
            # TODO: Fix KeyboardInterrupt errors
            try:
                grp_fn = os.setsid
            except AttributeError:
                grp_fn = None
            proc = subprocess.Popen("ipython notebook", shell=True, preexec_fn=grp_fn)
                #stdin=subprocess.PIPE, preexec_fn=grp_fn)
                #stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        except OSError:
            print "ERROR: Command `ipython notebook` not found."
            print "       If IPython or Anaconda is installed, check your PATH variable."
            sys.exit(1)

        # CLEAN EXIT AND SHUTDOWN OF IPYTHON NOTEBOOK
        def signal_handler(signal,frame):
            # Cross-Platform Compatability
            try:
                os.killpg(proc.pid, signal)
                proc.communicate()
            except AttributeError:
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])    
    
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
    

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("config_file", help="Path to Config File")
    args = parser.parse_args()
