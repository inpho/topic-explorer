"""
app.wsgi

This file contains the WSGI adapter for the topicexplorer, enabling it
to be embedded in Apache or another WSGI-compliant server. Run the module
`topicexplorer.apache` to be guided through the configuration process.

Two sets of configuration files are loaded in the following order:
1.  *Optional:* The configuration file located at the environment
    variable `TOPICEXPLORER_CONFIG`, which contains one key-value pair
    per line consisting of a process group identifier and an absolute 
    path to the topicexplorer configuration file or corpus directory.
    Ex:
    ```
    ap /home/jaimie/Topics/ap.ini
    sep /home/jaimie/Topics/sep.ini
    ```
2.  The directory `/var/www/topicexplorer/config/` is scanned for `.ini`
    files, loaded into the dictionary. These files are given priority.
"""
from argparse import ArgumentParser
from glob import iglob as glob
import os
import os.path

import mod_wsgi
import topicexplorer.server

# get process group to identify which config to use
_, group, k = mod_wsgi.process_group.split('.', 2)

# initalize configuration dictionary
config_path = dict()

# get master config file
configfile = os.environ.get('TOPICEXPLORER_CONFIG', None)
if configfile:
    with open(configfile) as config:
        for line in config:
            key, path = line.split(' ', 1)
            path = path.format(**os.environ)
            config_path[key] = os.path.abspath(path.strip())
elif not os.path.exists(configfile):
    # TODO: Convert to log message
    raise Exception("{} does not exist".format(configfile))
elif not configfile:
    # TODO: Convert to log message
    raise Exception("No TOPICEXPLORER_CONFIG environment variable set.")

# grab config files from "config" directory
for path in glob('/var/www/topicexplorer/config/*.ini'):
    key = os.path.basename(path).replace('.ini','')
    config_path[key] = path

# parse arguments for the server instance
parser = ArgumentParser()
topicexplorer.server.populate_parser(parser)
print config_path[group]
args = parser.parse_args([config_path[group], '-k', k])

# start the server
application = topicexplorer.server.main(args)

