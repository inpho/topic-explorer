"""
topicexplorer.lib.util contains some helper functions for command prompts, argparse, and globing
"""

import os, fnmatch
import os.path
from glob import glob

def is_valid_filepath(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


## Command Line Prompts
def overwrite_prompt(filename, default=True):
    if os.path.exists(filename):
        prompt_str = 'Overwrite {0}?'.format(filename)
        overwrite = bool_prompt(prompt_str, default=default)
        return overwrite
    else:
        return default

def bool_prompt(prompt_str, default=None):
    if default == True:
        default = 'y'
    elif default == False:
        default = 'n'

    result = prompt(prompt_str, options=['y','n'], default=default)

    if result == 'y':
        return True
    elif result == 'n':
        return False

def int_prompt(prompt_str, default=None, min=None, max=None):
    result = prompt(prompt_str, default=default)

    try:
        result = int(result)
    except:
        print "ERROR: You must enter a number."
        return int_prompt(prompt_str, default=default, min=min, max=max)
    if max and min and not (result <= max and result > min):
        print "ERROR: You must enter a number between {min} and {max}."\
             .format(min=min, max=max)
        return int_prompt(prompt_str, default=default, min=min, max=max)
    elif max and result > max:
        print "ERROR: You must enter a number less than {max}."\
             .format(min=min, max=max)
        return int_prompt(prompt_str, default=default, min=min, max=max)
    elif min and result <= min:
        print "ERROR: You must enter a number greater than {min}."\
             .format(min=min, max=max)
        return int_prompt(prompt_str, default=default, min=min, max=max)
    else:
        return result
            


def prompt(prompt, options=None, default=None):
    # Construct prompt
    prompt = "\n"+prompt

    if options:
        choices = options[:]
        if default and default in choices:
            default_idx = choices.index(default)
            choices[default_idx] = choices[default_idx].upper()
        prompt += " [{0}]".format('/'.join(choices))
    elif default:
        prompt += " [Default: {0}]".format(default)
    prompt += " "

    # Wait for valid response
    result = None
    while result is None or (options and result not in options):
        result = raw_input(prompt)
        result = result.lower().strip()
        if default and result == '':
            result = default

    return result



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

def isint(x):
    try:
        int(x)
        return True
    except (ValueError, TypeError):
        return False
