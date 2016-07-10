"""
app.wsgi

This file contains the WSGI adapter for the topicexplorer, enabling it
to be embedded in Apache or another WSGI-compliant server. Run the module
`topicexplorer.apache` to be guided through the configuration process.

The directory `TOPICEXPLORER_CONFIG_DIR` (Default: 
`/var/www/topicexplorer/config/`) is scanned for `.ini` files, each of
which is joined to the master url at `/FILENAME/`.
"""
from argparse import ArgumentParser
from glob import iglob as glob
import os
import os.path

import bottle
import topicexplorer.server

# initalize configuration dictionary
config = dict()

# get configuration directory
config_dir = os.environ.get('TOPICEXPLORER_CONFIG_DIR',
    '/var/www/topicexplorer/config/')

# grab config files from "config" directory
for path in glob(os.path.join(config_dir, '*.ini')):
    key = os.path.basename(path).replace('.ini','')
    config[key] = path

# create argument parser and default app
parser = ArgumentParser()
topicexplorer.server.populate_parser(parser)
application = bottle.default_app()

# append each model to the app
for model, path in config.iteritems():
    args = parser.parse_args([path])
    child_app = topicexplorer.server.main(args)
    application.mount('/{}/'.format(model), child_app)

