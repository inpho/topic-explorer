from ConfigParser import ConfigParser
import os, os.path
import socket
import signal, sys
from StringIO import StringIO
import subprocess
import time
import urllib
import webbrowser

from topicexplorer.lib.util import int_prompt, bool_prompt, is_valid_filepath

def main(args):
    # CONFIGURATION PARSING
    # load in the configuration file
    config = ConfigParser({
        'certfile' : None,
        'keyfile' : None,
        'ca_certs' : None,
        'ssl' : False,
        'port' : '8000',
        'host' : '0.0.0.0',
        'icons': 'link',
        'corpus_link' : None,
        'doc_title_format' : None,
        'doc_url_format' : None,
        'topic_range': None,
        'topics': None})
    config.read(args.config_file)

    if config.get('main', 'topic_range'):
        topic_range = map(int, config.get('main', 'topic_range').split(','))
        topic_range = range(*topic_range)
    if config.get('main', 'topics'):
        topic_range = eval(config.get('main', 'topics'))
    print topic_range

    # LAUNCHING SERVERS
    # Cross-platform compatability
    def get_log_file(k):
        if config.has_section('logging'):
            path = config.get('logging','path')
            path = path.format(k)
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            return open(path, 'a')
        else:
            return subprocess.PIPE


    def test_baseport(baseport, topic_range):
        try:
            host = config.get("www","host")
            if host == '0.0.0.0':
                host = 'localhost'
            for k in topic_range:
                port = baseport + k
                try:
                    s = socket.create_connection((host,port), 2)
                    s.close()
                    raise IOError("Socket connectable on port {0}".format(port))
                except socket.error:
                    pass
            return baseport
        except IOError:
            baseport = int_prompt(
                "Conflict on port {0}. Enter new base port: [CURRENT: {1}]"\
                    .format(port, baseport)) 
            return test_baseport(baseport)

    baseport = test_baseport(int(config.get("www","port").format(0)),
                             topic_range)

    # prompt to save
    if int(config.get("www","port").format(0)) != baseport:
        if bool_prompt("Change default baseport to {0}?".format(baseport),
                       default=True):
            config.set("www","port", baseport)

            # create deep copy of configuration
            # see http://stackoverflow.com/a/24343297
            config_string = StringIO()
            config.write(config_string)

            # skip DEFAULT section
            config_string.seek(0)
            idx = config_string.getvalue().index("[main]")
            config_string.seek(idx)

            # read deep copy
            new_config = ConfigParser()
            new_config.readfp(config_string)

            # write deep copy without DEFAULT section
            # this preserves DEFAULT for rest of program
            with open(args.config_file,'wb') as configfh:
                new_config.write(configfh)


    try:
        grp_fn = os.setsid
    except AttributeError:
        grp_fn = None
    procs = [subprocess.Popen("vsm serve -k {k} -p {port} {config_file}".format(
        k=k, port=(baseport+k), config_file=args.config_file),
        shell=True, stdout=get_log_file(k), stderr=subprocess.STDOUT,
        preexec_fn=grp_fn) for k in topic_range]

    print "pid","port"
    for proc,k in zip(procs, topic_range):
        port = baseport + k
        host = config.get("www","host")
        print proc.pid, "http://{host}:{port}/".format(host=host,port=port)


    # CLEAN EXIT AND SHUTDOWN OF SERVERS
    def signal_handler(signal,frame):
        print "\n"
        for p in procs:
            print "killing", p.pid
            # Cross-Platform Compatability
            try:
                os.killpg(p.pid, signal)
            except AttributeError:
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])    

        sys.exit()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    port = baseport + topic_range[0]
    host = config.get("www","host")
    if host == '0.0.0.0':
        host = 'localhost'
    url = "http://{host}:{port}/".format(host=host,port=port)

    # TODO: Add enhanced port checking
    while True:
        try:
            urllib.urlopen(url)
            print "Server successfully started"
            break
        except:
            time.sleep(1)
    if args.browser:
        webbrowser.open(url)
        print "TIP: Browser launch can be disabled with the '--no-browser' argument:"
        print "vsm launch --no-browser", args.config_file, "\n"

    print "Press Ctrl+C to shutdown the Topic Explorer server"
    # Cross-platform Compatability
    try:
        signal.pause()
    except AttributeError:
        # Windows hack
        while True:
            time.sleep(1)

def populate_parser(parser):
    parser.add_argument('config_file', help="Configuration file path",
        type=lambda x: is_valid_filepath(parser, x))
    parser.add_argument('--no-browser', dest='browser', action='store_false')

if __name__ == '__main__':
    from argparse import ArgumentParser

    # ARGUMENT PARSING
    def is_valid_filepath(parser, arg):
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!" % arg)
        else:
            return arg
    
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
