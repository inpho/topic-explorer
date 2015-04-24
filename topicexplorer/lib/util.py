import os, fnmatch
import os.path
from glob import glob

def is_valid_filepath(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

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

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def contains_pattern(directory, pattern):
    try:
        find_files(directory, pattern).next()
        return True
    except StopIteration:
        return False
