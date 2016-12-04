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
from functools import partial
from glob import iglob as glob
import os
import os.path
from pkg_resources import resource_filename
import shutil

import bottle
import topicexplorer.server

# initalize configuration dictionary
config = dict()

# get configuration directory
CONFIG_DIR = os.environ.get('TOPICEXPLORER_CONFIG_DIR',
    '/var/www/topicexplorer/config/')

# grab config files from "config" directory
for path in glob(os.path.join(CONFIG_DIR, '*.ini')):
    key = os.path.basename(path).replace('.ini','')
    config[key] = path

# Create global static file serving - helps with caching
WWW_DIR = os.environ.get('TOPICEXPLORER_WWW_DIR',
    '/var/www/topicexplorer/www/')
STATIC_DIR = resource_filename('topicexplorer.server', '../www/')

def send_static(filename):
    # override for a particular model, just had the wrong path
    if filename in config.keys():
        bottle.redirect('/{}/'.format(filename), 307)

    if filename.startswith('/'):
        filename = filename[1:]

    www_path = os.path.join(WWW_DIR, filename)
    static_path = os.path.join(STATIC_DIR, filename)

    # reinit if these are directories
    if os.path.isdir(www_path) and os.path.isdir(static_path):
        filename = os.path.join(filename, 'index.html')
        www_path = os.path.join(WWW_DIR, filename)
        static_path = os.path.join(STATIC_DIR, filename)

    if os.path.exists(www_path):
        root = WWW_DIR
    else:
        root = resource_filename('topicexplorer.server', '../www/')

    return bottle.static_file(filename, root=root)

def static_child(filename, model):
    return send_static(os.path.join('/{}/'.format(model), filename))

# create argument parser and default app
parser = ArgumentParser()
topicexplorer.server.populate_parser(parser)
application = bottle.default_app()

# append each model to the app
for model, path in config.iteritems():
    args = parser.parse_args([path, '--no-browser'])
    try:
        child_app = topicexplorer.server.create_app(args)

        child_app.route('/<filename:path>', 'GET',
            partial(topicexplorer.server._set_acao_headers(static_child),
                    model=model))

        # Override default route if custom index is defined.
        index_path = model + '/index.html'
        www_path = os.path.join(WWW_DIR, index_path)
        static_path = os.path.join(STATIC_DIR, index_path)
        if os.path.exists(www_path) or os.path.exists(static_path):
            child_app.route('/', 'GET',
                partial(topicexplorer.server._set_acao_headers(static_child),
                        model=model, filename='/{}/index.html'.format(model)))

        application.mount('/{}/'.format(model), child_app)

    except Exception as e:
        print "Could not load", model
        import traceback
        import sys
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)


        @application.route('/{}/'.format(model))
        def raise_error():
            traceback.print_exc()
            raise e

        @application.route('/{}/<filename:path>'.format(model))
        def raise_error(filename):
            traceback.print_exc()
            raise e


application.route('/<filename:path>', 'GET',
    topicexplorer.server._set_acao_headers(send_static))

@application.route('/')
def index():
    return send_static('index.html')
