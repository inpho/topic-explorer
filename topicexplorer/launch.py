from ConfigParser import ConfigParser
import os, os.path
import signal, sys
import subprocess
import time
import urllib
import webbrowser

def main(args):
    # CONFIGURATION PARSING
    # load in the configuration file
    config = ConfigParser({
        'certfile' : None,
        'keyfile' : None,
        'ca_certs' : None,
        'ssl' : False,
        'port' : '8{0:03d}',
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

    try:
        grp_fn = os.setsid
    except AttributeError:
        grp_fn = None
    procs = [subprocess.Popen("vsm serve -k %d %s" % (k, args.config_file),
        shell=True, stdout=get_log_file(k), stderr=subprocess.STDOUT,
        preexec_fn=grp_fn) for k in topic_range]

    print "pid","port"
    for proc,k in zip(procs, topic_range):
        port = config.get("main","port").format(k)
        host = config.get("main","host")
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

    port = config.get("main","port").format(topic_range[0])
    host = config.get("main","host")
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

if __name__ == '__main__':
    from argparse import ArgumentParser

    # ARGUMENT PARSING
    def is_valid_filepath(parser, arg):
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!" % arg)
        else:
            return arg
    
    parser = ArgumentParser()
    parser.add_argument('config', type=lambda x: is_valid_filepath(parser, x),
        help="Configuration file path")
    parser.add_argument('--no-browser', dest='browser', action='store_false')
    args = parser.parse_args()

    main(args)
