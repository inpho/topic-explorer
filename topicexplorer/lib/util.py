"""
topicexplorer.lib.util contains some helper functions for command prompts, argparse, and globing
"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import input
from past.builtins import basestring

from codecs import open
import fnmatch
from glob import glob
import os
import os.path
from pkg_resources import resource_filename
import shutil
import sys


def safe_symlink(srcpath, linkpath):
    """
    Provides support for symlink if OS supports it, otherwise copies the file.
    Largely a nice workaround for Windows.
    """
    if os.name == "nt":
        def symlink_ms(source, link_name):
            import ctypes
            csl = ctypes.windll.kernel32.CreateSymbolicLinkW
            csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
            csl.restype = ctypes.c_ubyte
            flags = 1 if os.path.isdir(source) else 0
            try:
                if csl(link_name, source.replace('/', '\\'), flags) == 0:
                    raise ctypes.WinError()
            except:
                shutil.copyfile(source, link_name)

        os.symlink = symlink_ms

    srcpath = os.path.abspath(srcpath)
    linkpath = os.path.abspath(linkpath)
    os.symlink(srcpath, linkpath)


def is_valid_filepath(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg


def is_valid_configfile(parser, arg):
    if not arg.endswith('.ini'):
        if os.path.isdir(arg):
            print("{0} is a directory, using the config file {0}.ini".format(arg))
            if arg.endswith('/'):
                arg = arg[:-1]
        else:
            print("{0} is missing the '.ini' extension, using the config file {0}.ini".format(arg))
        arg = arg + '.ini'

    if os.path.exists(arg):
        from configparser import RawConfigParser as ConfigParser
        config = ConfigParser()
        try:
            with open(arg, encoding='utf-8') as configfile:
                config.read_file(configfile)
            return arg
        except:
            parser.error("Invalid config file {0}".format(arg))
    else:
        parser.error("The file %s does not exist!" % arg)


def listdir_nohidden(path, recursive=False):
    if recursive:
        for root, dirs, files in os.walk(path):
            for f in files:
                if not f.startswith('.'):
                    yield os.path.join(root, f)
    else:
        for f in os.listdir(path):
            if not f.startswith('.'):
                yield f


# Command Line Prompts
def overwrite_prompt(filename, default=True):
    if os.path.exists(filename):
        prompt_str = 'Overwrite {0}?'.format(filename)
        overwrite = bool_prompt(prompt_str, default=default)
        return overwrite
    else:
        return True


def bool_prompt(prompt_str, default=None):
    if default is True:
        default = 'y'
    elif default is False:
        default = 'n'

    result = prompt(prompt_str, options=['y', 'n'], default=default)

    if result == 'y':
        return True
    elif result == 'n':
        return False


def int_prompt(prompt_str, default=None, min=None, max=None):
    result = prompt(prompt_str, default=default)

    try:
        result = int(result)
    except:
        print("ERROR: You must enter a number.")
        return int_prompt(prompt_str, default=default, min=min, max=max)
    if max and min and not (result <= max and result > min):
        print("ERROR: You must enter a number between {min} and {max}."\
            .format(min=min, max=max))
        return int_prompt(prompt_str, default=default, min=min, max=max)
    elif max and result > max:
        print("ERROR: You must enter a number less than {max}."\
            .format(min=min, max=max))
        return int_prompt(prompt_str, default=default, min=min, max=max)
    elif min and result <= min:
        print("ERROR: You must enter a number greater than {min}."\
            .format(min=min, max=max))
        return int_prompt(prompt_str, default=default, min=min, max=max)
    else:
        return result


def prompt(prompt, options=None, default=None):
    # Construct prompt
    prompt = "\n" + prompt

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
        result = input(prompt)
        result = result.lower().strip()
        if default and result == '':
            result = default

    return result


def find_files(directory, pattern, include_hidden=False):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                if not include_hidden and basename.startswith('.'):
                    pass
                else:
                    yield filename


def contains_pattern(directory, pattern):
    try:
        next(find_files(directory, pattern))
        return True
    except StopIteration:
        return False


def isint(x):
    try:
        int(x)
        return True
    except (ValueError, TypeError):
        return False

def get_static_resource_path(path):
    if os.path.exists(path):
        return os.path.abspath(path)
    elif os.path.exists(os.path.join(sys.prefix, path)):
        return os.path.abspath(os.path.join(sys.prefix, path))
    elif os.path.exists(os.path.join(
             os.path.join(sys.prefix, 'opt/topicexplorer'), path)):
        return os.path.abspath(os.path.join(
            os.path.join(sys.prefix, 'opt/topicexplorer'), path))
    elif os.path.exists(resource_filename(__name__, path)):
        return resource_filename(__name__, path)
    elif os.path.exists(resource_filename(__name__, '../' + path)):
        return resource_filename(__name__, '../' + path)
    elif os.path.exists(resource_filename(__name__, '../../' + path)):
        return resource_filename(__name__, '../../' + path)
    else:
        raise OSError("File not found: {}".format(path))

