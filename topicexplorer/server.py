from codecs import open
from ConfigParser import RawConfigParser as ConfigParser, NoOptionError
import csv
from datetime import datetime, timedelta
from importlib import import_module
import json
import itertools
import os.path
import re
import socket
from urllib2 import unquote
from StringIO import StringIO

from bottle import request, response, route, run, static_file
from topicexplorer.lib.ssl import SSLWSGIRefServer
from topicexplorer.lib.util import int_prompt, bool_prompt, is_valid_filepath, is_valid_configfile

import random
import pystache

def _set_acao_headers(f):
    """
    Decorator to set Access-Control-Allow-Origin headers to enable cross-InPhO
    embedding of Topic Explorer bars.
    """
    def set_header(*args, **kwargs):
        host = request.get_header('Origin')
        if host and 'cogs.indiana.edu' in host:
            response.headers['Access-Control-Allow-Origin'] = host
        return f(*args, **kwargs)
    return set_header

def _cache_date(days=1):
    time = datetime.now() + timedelta(days=days)
    return time.strftime("%a, %d %b %Y %I:%M:%S GMT")

@route('/doc_topics/<doc_id>')
@_set_acao_headers
def doc_topic_csv(doc_id):
    response.content_type = 'text/csv; charset=UTF8'

    doc_id = unquote(doc_id)

    data = lda_v.doc_topics(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['topic','prob'])
    writer.writerows([(t, "%6f" % p) for t,p in data])

    return output.getvalue()

@route('/docs/<doc_id>')
@_set_acao_headers
def doc_csv(doc_id, threshold=0.2):
    response.content_type = 'text/csv; charset=UTF8'
    
    doc_id = unquote(doc_id)

    data = lda_v.sim_doc_doc(doc_id, label_fn=id_fn)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['doc','prob'])
    writer.writerows([(d, "%6f" % p) for d,p in data if p > threshold])

    return output.getvalue()

@route('/topics/<topic_no>.json')
@_set_acao_headers
def topic_json(topic_no, N=40):
    response.content_type = 'application/json; charset=UTF8'
    try:
        N = int(request.query.n)
    except:
        pass

    if N > 0:
        data = lda_v.dist_top_doc([int(topic_no)], label_fn=id_fn)[:N]
    else:
        data = lda_v.dist_top_doc([int(topic_no)], label_fn=id_fn)[N:]
        data = reversed(data)
    
    docs = [doc for doc,prob in data]
    doc_topics_mat = lda_v.doc_topics(docs)
    docs = get_docs(docs, id_as_key=True)

    js = []
    for doc_prob, topics in zip(data, doc_topics_mat):
        doc, prob = doc_prob
        struct = docs[doc]
        struct.update({'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in topics])})
        js.append(struct)

    return json.dumps(js)

@route('/docs_topics/<doc_id:path>.json')
@_set_acao_headers
def doc_topics(doc_id, N=40):
    try:
        N = int(request.query.n)
    except:
        pass

    doc_id = unquote(doc_id)
    print doc_id

    response.content_type = 'application/json; charset=UTF8'


    if N > 0:
        data = lda_v.dist_doc_doc(doc_id, label_fn=id_fn)[:N]
    else:
        data = lda_v.dist_doc_doc(doc_id, label_fn=id_fn)[N:]
        data = reversed(data)
   
    docs = [doc for doc,prob in data]
    doc_topics_mat = lda_v.doc_topics(docs)
    docs = get_docs(docs, id_as_key=True)

    js = []
    for doc_prob, topics in zip(data, doc_topics_mat):
        doc, prob = doc_prob
        struct = docs[doc]
        struct.update({'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in topics])})
        js.append(struct)

    return json.dumps(js)

@route('/word_docs.json')
@_set_acao_headers
def word_docs(N=40):
    try:
        N = int(request.query.n)
    except:
        pass
    try: 
        query = request.query.q.lower().split('|')
    except:
        raise Exception('Must specify a query') 

    response.content_type = 'application/json; charset=UTF8'

    query = [word for word in query if word in lda_c.words]
    
    # abort if there are no terms in the query
    if not query:
        response.status = 400 # Bad Request
        return "Search terms not in model"

    topics = lda_v.dist_word_top(query, show_topics=False)
    data = lda_v.dist_top_doc(topics['i'], 
               weights=(topics['value'].max() - topics['value']), label_fn=id_fn)

    if N > 0:
        data = data[:N]
    else:
        data = data[N:]
        data = reversed(data)
   
    docs = [doc for doc,prob in data]
    doc_topics_mat = lda_v.doc_topics(docs)
    docs = get_docs(docs, id_as_key=True)

    js = []
    for doc_prob, topics in zip(data, doc_topics_mat):
        doc, prob = doc_prob
        struct = docs[doc]
        struct.update({'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in topics])})
	js.append(struct)

    return json.dumps(js)

@route('/topics.json')
@_set_acao_headers
def topics():
    from topicexplorer.lib.color import rgb2hex

    response.content_type = 'application/json; charset=UTF8'
    response.set_header('Expires', _cache_date())

    # populate partial jsd values
    data = lda_v.topic_jsds()

    js = {}
    for rank,topic_H in enumerate(data):
        topic, H = topic_H
        js[str(topic)] = {
            "H" : H, 
            "color" : rgb2hex(colors[topic])
        }
    
    # populate word values
    data = lda_v.topics()
    for i,topic in enumerate(data):
        js[str(i)].update({'words' : dict([(w, p) for w,p in topic[:10]])})

    return json.dumps(js)

@route('/docs.json')
@_set_acao_headers
def docs(docs=None, q=None):
    response.content_type = 'application/json; charset=UTF8'
    response.set_header('Expires', _cache_date())
    
    try:
        if request.query.q:
            q = unquote(request.query.q)
    except:
        pass

    try: 
        if request.query.id:
            docs = [unquote(request.query.id)]
    except:
        pass
    
    try: 
        response.set_header('Expires', 0)
        response.set_header('Pragma', 'no-cache')
        response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        if request.query.random:
            docs = [random.choice(lda_v.corpus.view_metadata(context_type)[doc_label_name(context_type)])]
    except:
        pass

    js = get_docs(docs, query=q)

    return json.dumps(js)

def get_docs(docs=None, id_as_key=False, query=None):
    ctx_md = lda_v.corpus.view_metadata(context_type)
    
    if docs:
        # filter to metadata for selected docs
        ids = [lda_v.corpus.meta_int(context_type, {doc_label_name(context_type) : doc} ) for doc in docs]
        ctx_md = ctx_md[ids]
    else:
        #get metadata for all documents
        docs = lda_v.corpus.view_metadata(context_type)[doc_label_name(context_type)]
    
    js = dict() if id_as_key else list()

    for doc, md in zip(docs, ctx_md):
        if query is None or query.lower() in label(doc).lower():
            struct = {
                'id': doc,
                'label' : label(doc),
                'metadata' : dict(zip(md.dtype.names, [unicode(m) for m in md])) }
            if id_as_key:
                js[doc] = struct
            else:
                js.append(struct)

    return js

def main(args):
    from pkg_resources import resource_filename
    from topicexplorer.lib.color import get_topic_colors, rgb2hex

    from vsm.corpus import Corpus
    from vsm.model.lda import LDA
    from vsm.viewer.ldacgsviewer import LdaCgsViewer as LDAViewer
    from vsm.viewer.wrappers import doc_label_name as _doc_label_name

    global context_type, lda_c, lda_m, lda_v 
    global label, id_fn, doc_label_name
    global corpus_path

    doc_label_name = _doc_label_name

    # load in the configuration file
    config = ConfigParser({
        'certfile' : None,
        'keyfile' : None,
        'ca_certs' : None,
        'ssl' : False,
        'port' : '8000',
        'host' : '0.0.0.0',
        'topic_range' : '{0},{1},1'.format(args.k, args.k+1),
        'icons': 'link',
        'corpus_link' : None,
        'doc_title_format' : None,
        'doc_url_format' : None,
        'raw_corpus' : None,
        'fulltext' : 'false',
        'topics': None})
    config.read(args.config)

    # path variables
    path = config.get('main', 'path')
    context_type = config.get('main', 'context_type')
    corpus_file = config.get('main', 'corpus_file')
    model_pattern = config.get('main', 'model_pattern') 

    # automatic port assignment

    def test_port(port):
        try:
            host = args.host or config.get("www","host")
            if host == '0.0.0.0':
                host = 'localhost'
            try:
                s = socket.create_connection((host,port), 2)
                s.close()
                raise IOError("Socket connectable on port {0}".format(port))
            except socket.error:
                pass
            return port
        except IOError:
            port = int_prompt(
                "Conflict on port {0}. Enter new port:".format(port)) 
            return test_port(port)

    port = args.port or int(config.get('www','port').format(0)) + args.k
    port = test_port(port)
    
    # prompt to save
    if (int(config.get("www","port").format(0)) + args.k) != port:
        if bool_prompt("Change default baseport to {0}?".format(port - args.k),
                       default=True):
            config.set("www","port", str(port - args.k))

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
            with open(args.config, 'wb') as configfh:
                new_config.write(configfh)


    # hostname assignment
    host = args.host or config.get('www','host')

    # LDA objects
    lda_c = Corpus.load(corpus_file)
    lda_m = None
    lda_v = None
    colors = None
    def load_model(k):
        global lda_m, lda_v, colors
        lda_m = LDA.load(model_pattern.format(k))
        lda_v = LDAViewer(lda_c, lda_m)
        colors = dict(get_topic_colors(lda_v))

    load_model(args.k)

    # label function imports
    try:
        label_module = config.get('main', 'label_module')
        label_module = import_module(label_module)
        print "imported label module"
        label_module.init(lda_v, config, args)
    except (ImportError, NoOptionError, AttributeError):
        pass

    try:
        label = label_module.label
        print "imported label function"
    except (AttributeError, UnboundLocalError):
        label = lambda x: x
        print "using default label function"
        
    try:
        id_fn = label_module.id_fn
        print "imported id function"
    except (AttributeError, UnboundLocalError):
        id_fn = lambda metadata: metadata[doc_label_name(lda_v.model.context_type)]
        print "using default id function"

    corpus_path = config.get('main', 'raw_corpus')
    if args.fulltext or config.getboolean('www','fulltext'):
        @route('/fulltext/<doc_id:path>')
        @_set_acao_headers
        def get_doc(doc_id):
            import re
            doc_id = unquote(doc_id).decode('utf-8')
            pdf_path = os.path.join(corpus_path, re.sub('txt$','pdf', doc_id))
            if os.path.exists(pdf_path):
                doc_id = re.sub('txt$','pdf', doc_id)
    
            return static_file(doc_id, root=corpus_path)

    config_icons = config.get('www','icons').split(",")
    if args.fulltext or config.getboolean('www','fulltext'):
        if ('fulltext' not in config_icons and
            'fulltext-inline' not in config_icons):
            config_icons.insert(0,'fulltext')
    

    @route('/icons.js')
    def icons():
        with open(resource_filename(__name__, '../www/icons.js')) as icons:
            text = '{0}\n var icons = {1};'\
                .format(icons.read(), json.dumps(config_icons))
        return text


    # index page parameterization
    corpus_name = config.get('www','corpus_name')
    corpus_link = config.get('www','corpus_link')
    doc_title_format = config.get('www', 'doc_title_format')
    doc_url_format = config.get('www', 'doc_url_format')

    if config.get('main', 'topic_range'):
        topic_range = map(int, config.get('main', 'topic_range').split(','))
        topic_range = range(*topic_range)
    if config.get('main', 'topics'):
        topic_range = eval(config.get('main', 'topics'))
    topic_range = [{'k' : k, 'port' : port - args.k + k} 
                        for k in topic_range] 

    renderer = pystache.Renderer(escape=lambda u: u)

    @route('/')
    def index():
        response.set_header('Expires', _cache_date())

        with open(resource_filename(__name__, '../www/index.mustache.html'),
                  encoding='utf-8') as tmpl_file:
            template = tmpl_file.read()
        return renderer.render(template, 
            {'corpus_name' : corpus_name,
             'corpus_link' : corpus_link,
             'context_type' : context_type,
             'topic_range' : topic_range,
             'doc_title_format' : doc_title_format,
             'doc_url_format' : doc_url_format})



    @route('/<filename:path>')
    @_set_acao_headers
    def send_static(filename):
        return static_file(filename, root=resource_filename(__name__, '../www/'))


    if args.ssl or config.get('main', 'ssl'):
        certfile = args.certfile or config.get('ssl', 'certfile')
        keyfile = args.keyfile or config.get('ssl', 'keyfile')
        ca_certs = args.ca_certs or config.get('ssl', 'ca_certs')

        run(host=host, port=port, server=SSLWSGIRefServer,
            certfile=certfile, keyfile=keyfile, ca_certs=ca_certs)
    else:
        run(host=host, port=port)

def populate_parser(parser):
    parser.add_argument('config', type=lambda x: is_valid_configfile(parser, x),
        help="Configuration file path")
    parser.add_argument('-k', type=int, required=True,
        help="Number of Topics")
    parser.add_argument('-p', dest='port', type=int, 
        help="Port Number", default=None)
    parser.add_argument('--host', default=None, help='Hostname')
    parser.add_argument('--fulltext', action='store_true', 
        help='Serve raw corpus files.')
    parser.add_argument('--bibtex', default=None, 
        type=lambda x: is_valid_filepath(parser, x),
        help='BibTeX library location')
    parser.add_argument('--ssl', action='store_true',
        help="Use SSL (must specify certfile, keyfile, and ca_certs in config)")
    parser.add_argument('--ssl-certfile', dest='certfile', nargs="?",
        const='server.pem', default=None,
        type=lambda x: is_valid_filepath(parser, x),
        help="SSL certificate file")
    parser.add_argument('--ssl-keyfile', dest='keyfile', default=None,
        type=lambda x: is_valid_filepath(parser, x),
        help="SSL certificate key file")
    parser.add_argument('--ssl-ca', dest='ca_certs', default=None,
        type=lambda x: is_valid_filepath(parser, x),
        help="SSL certificate authority file")

if __name__ == '__main__':
    from argparse import ArgumentParser
    
    # argument parsing
    parser = ArgumentParser()
    populate_parser(parser)
    args = parser.parse_args()
    
    main(args)
