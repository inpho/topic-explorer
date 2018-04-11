from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

from configparser import ConfigParser

def read(config_file):
    config = ConfigParser({"htrc": False,
                           "sentences": False})
    config.read(config_file)

    return config