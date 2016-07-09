from argparse import ArgumentParser
import os
import os.path

import bottle
import topicexplorer.server

parser = ArgumentParser()
topicexplorer.server.populate_parser(parser)
args = parser.parse_args(['/home/jaimie/workspace/topic-explorer/ap.ini', '-k', '20'])

topicexplorer.server.main(args)

application = bottle.default_app()

