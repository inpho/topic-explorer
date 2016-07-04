from ConfigParser import ConfigParser
import os, os.path
import platform
import socket
import signal, sys
from StringIO import StringIO
import subprocess
import time
import urllib
import webbrowser

from topicexplorer.lib.util import int_prompt, bool_prompt, is_valid_configfile

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
        'fulltext' : 'false',
        'raw_corpus': None,
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


    def test_baseport(host, baseport, topic_range):
        try:
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
            return test_baseport(host, baseport, topic_range)

    host = config.get("www","host")
    if host == '0.0.0.0':
        host = socket.gethostname()

    baseport = int(config.get("www","port").format(0))
    baseport = test_baseport(host, baseport, topic_range)

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
    fulltext = '--fulltext' if args.fulltext else ''
    procs = [subprocess.Popen("topicexplorer serve -k {k} -p {port} {config_file} {fulltext} --no-browser".format(
        k=k, port=(baseport+k), config_file=args.config_file,fulltext=fulltext),
        shell=True, stdout=get_log_file(k), stderr=subprocess.STDOUT,
        preexec_fn=grp_fn) for k in topic_range]

    print "pid","port"
    for proc,k in zip(procs, topic_range):
        port = baseport + k
        print proc.pid, "http://{host}:{port}/".format(host=host,port=port)


    # CLEAN EXIT AND SHUTDOWN OF SERVERS
    def signal_handler(signal,frame):
        print "\n"
        for p, k in zip(procs, topic_range):
            print "Stopping {}-topic model (Process ID: {})".format(k, p.pid)
            # Cross-Platform Compatability
            if platform.system() == 'Windows':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)],
                        stdout=open(os.devnull), stderr=open(os.devnull))
            else:
                os.killpg(p.pid, signal)

        sys.exit()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    port = baseport + topic_range[0]
    url = "http://{host}:{port}/".format(host=host,port=port)

    # TODO: Add enhanced port checking
    while True:
        wait_count = 0
        try:
            urllib.urlopen(url)
            print "Server successfully started"
            break
        except:
            time.sleep(1)
            wait_count += 1

        if wait_count == 60:
            print "\nLaunching the server seems to be taking a long time."
            print "This may be due to loading in a large corpus."

            print "\nTo test launching a single model, press Ctrl+C to abort launch,"
            print "then use the `serve` command to find the error message:"
            print "\ttopicexplorer serve {config} -k {k}".format(
                config=args.config_file, k=topic_range[0])
    
        for proc,k in zip(procs, topic_range):
            if proc.poll() is not None:
                print "\nAn error has occurred launching the {}-topic model.".format(k)
                try:
                    with get_log_file(k) as logfile:
                        print "A log has been written to: {}\n".format(logfile.name)
                except AttributeError:
                    # No log file, things are a-ok.
                    pass

                print "Use the `serve` command to debug errors:"
                print "\ttopicexplorer serve {config} -k {k}".format(config=args.config_file, k=k)
                for p in procs:
                    if p.poll() is None:
                        try:
                            os.killpg(p.pid, signal.SIGTERM)
                        except AttributeError:
                            # Cross-Platform Compatability
                            subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])    
    
                sys.exit(1)

    if args.browser:
        webbrowser.open(url)
        print "TIP: Browser launch can be disabled with the '--no-browser' argument:"
        print "topicexplorer launch --no-browser", args.config_file, "\n"

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
        type=lambda x: is_valid_configfile(parser, x))
    parser.add_argument('--no-browser', dest='browser', action='store_false')
    parser.add_argument('--fulltext', action='store_true',
        help='Serve raw corpus files.')

if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()

    main(args)
