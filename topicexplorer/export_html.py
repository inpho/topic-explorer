from argparse import ArgumentParser
from multiprocessing import Process
import os
import os.path
import shutil
import sys
if sys.version_info[0] == 2:
    import backports.tempfile
import tempfile
from zipfile import ZipFile

from webtest import TestApp

import topicexplorer.server
from topicexplorer.lib.util import get_static_resource_path, is_valid_configfile

def main(args):
    server_parser = ArgumentParser()
    topicexplorer.server.populate_parser(server_parser)
    
    server_args = server_parser.parse_args([args.config_file, '--no-browser'])
    app = topicexplorer.server.create_app(server_args)
    topics = app.topic_range
    
    app = TestApp(app)

    if sys.version_info[0] == 2:
        TD = backports.tempfile.TemporaryDirectory
    else:
        TD = tempfile.TemporaryDirectory
    with TD(prefix='vsm-') as OUTPUT_DIR:
        files = []
        output = os.path.join(OUTPUT_DIR, 'topics.html')
        with open(output, 'w') as outfile:
            outfile.write(app.get('/topics.local.html').text)
        files.append(output)

        output = os.path.join(OUTPUT_DIR, 'cluster.csv')
        with open(output, 'w') as outfile:
            outfile.write(app.get('/cluster.csv').text)
        files.append(output)

        for k in topics:
            k_output = os.path.join(OUTPUT_DIR, str(k))
            if not os.path.exists(k_output):
                os.makedirs(k_output)
            k_output = os.path.join(k_output, 'topics.json')
            with open(k_output, 'w') as outfile:
                outfile.write(app.get('/{}/topics.json'.format(k)).text)
            files.append(k_output)

        # make sure the directories are created
        dirname = os.path.dirname(args.output)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        # output path massaging
        if os.path.isdir(args.output):
            # make sure we've actually got a zipfile to put there
            args.output += 'topics.html.zip'
        elif not args.output.endswith('.zip'):
            # make sure we've got a zipfile
            args.output += '.zip'

        ZIPFILE = args.output
        TOPICS_ZIP = get_static_resource_path('topics.zip')
        shutil.copyfile(TOPICS_ZIP, ZIPFILE)
        with ZipFile(ZIPFILE, 'a') as zipfile:
            for f in files:
                zipfile.write(f, arcname=f.replace(OUTPUT_DIR, ''))

def populate_parser(parser):
    parser.add_argument('config_file', help='Topic Explorer ini file',
                        type=lambda x: is_valid_configfile(parser, x))
    parser.add_argument('-o', '--output', default='topics.html.zip',
                        help='Output file [Default: topics.html.zip]')
    return parser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser = populate_parser(parser)
    args = parser.parse_args()

    main(args)

