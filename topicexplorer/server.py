from codecs import open
from ConfigParser import ConfigParser
import csv
from datetime import datetime, timedelta
from importlib import import_module
import json
import itertools
import os.path
from pkg_resources import resource_filename
import re
from StringIO import StringIO

from vsm.corpus import Corpus
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer
from vsm.viewer.wrappers import doc_label_name

from bottle import request, response, route, run, static_file
from topicexplorer.lib.ssl import SSLWSGIRefServer

import pystache
import topicexplorer.lib.color as colorlib

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

    data = lda_v.sim_doc_doc(doc_id)

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
        data = lda_v.dist_top_doc([int(topic_no)])[:N]
    else:
        data = lda_v.dist_top_doc([int(topic_no)])[N:]
        data = reversed(data)
    
    docs = [doc for doc,prob in data]
    doc_topics_mat = lda_v.doc_topics(docs)

    js = []
    for doc_prob, topics in zip(data, doc_topics_mat):
        doc, prob = doc_prob
        js.append({'doc' : doc, 'label': label(doc), 'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in topics])})

    return json.dumps(js)

@route('/docs_topics/<doc_id>.json')
@_set_acao_headers
def doc_topics(doc_id, N=40):
    try:
        N = int(request.query.n)
    except:
        pass

    response.content_type = 'application/json; charset=UTF8'

    if N > 0:
        data = lda_v.dist_doc_doc(doc_id)[:N]
    else:
        data = lda_v.dist_doc_doc(doc_id)[N:]
        data = reversed(data)
   
    docs = [doc for doc,prob in data]
    doc_topics_mat = lda_v.doc_topics(docs)

    js = []
    for doc_prob, topics in zip(data, doc_topics_mat):
        doc, prob = doc_prob
        js.append({'doc' : doc, 'label': label(doc), 'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in topics])})

    return json.dumps(js)

@route('/topics.json')
@_set_acao_headers
def topics():
    response.content_type = 'application/json; charset=UTF8'
    response.set_header('Expires', _cache_date())

    # populate entropy values
    data = lda_v.topic_oscillations()

    colors = [itertools.cycle(cs) for cs in zip(*colorlib.brew(3,n_cls=4))]
    factor = len(data) / len(colors)

    js = {}
    for rank,topic_H in enumerate(data):
        topic, H = topic_H
        js[str(topic)] = {
            "H" : H, 
            "color" : colors[min(rank / factor, len(colors)-1)].next()
        }
    
    # populate word values
    data = lda_v.topics()
    for i,topic in enumerate(data):
        js[str(i)].update({'words' : dict([(w, p) for w,p in topic[:10]])})

    return json.dumps(js)

@route('/docs.json')
@_set_acao_headers
def docs():
    response.content_type = 'application/json; charset=UTF8'
    response.set_header('Expires', _cache_date())

    docs = lda_v.corpus.view_metadata(context_type)[doc_label_name(context_type)]
    js = list()
    for doc in docs:
        js.append({
            'id': doc,
            'label' : label(doc)
        })

    return json.dumps(js)

def main(args):
    global context_type, lda_c, lda_m, lda_v, label
    # load in the configuration file
    config = ConfigParser({
        'certfile' : None,
        'keyfile' : None,
        'ca_certs' : None,
        'ssl' : False,
        'port' : '8{0:03d}',
        'host' : '0.0.0.0',
        'topic_range' : '{0},{1},1'.format(args.k, args.k+1),
        'icons': 'link',
        'corpus_link' : None,
        'doc_title_format' : None,
        'doc_url_format' : None,
        'topic_range': None,
        'topics': None})
    config.read(args.config)

    # path variables
    path = config.get('main', 'path')
    context_type = config.get('main', 'context_type')
    corpus_file = config.get('main', 'corpus_file')
    model_pattern = config.get('main', 'model_pattern') 

    # automatic port assignment
    if args.port:
        port = args.port
        print port, "auto port"
    else:
        port = config.get('main','port').format(args.k)
        print port

    # hostname assignment
    if args.host:
        host = args.host
    else:
        host = config.get('main','host')

    # LDA objects
    lda_c = Corpus.load(corpus_file)
    lda_m = None
    lda_v = None
    def load_model(k):
        global lda_m, lda_v
        lda_m = LCM.load(model_pattern.format(k))
        lda_v = LDAViewer(lda_c, lda_m)

    load_model(args.k)

    # label function imports
    try:
        label_module = config.get('main', 'label_module')
        label_module = import_module(label_module)
        try:
            label_module.init(config.get('main','path'))
        except:
            pass

        label = label_module.label
    except:
        label = lambda x: x

    config_icons = config.get('www','icons').split(",")

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
    topic_range = [{'k' : k, 'port' : config.get('main','port').format(k)} 
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


if __name__ == '__main__':
    from argparse import ArgumentParser

    def is_valid_filepath(parser, arg):
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!" % arg)
        else:
            return arg
    
    # argument parsing
    parser = ArgumentParser()
    parser.add_argument('config', type=lambda x: is_valid_filepath(parser, x),
        help="Configuration file path")
    parser.add_argument('-k', type=int, required=True,
        help="Number of Topics")
    parser.add_argument('-p', dest='port', type=int, 
        help="Port Number", default=None)
    parser.add_argument('--host', default=None, help='Hostname')
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
    args = parser.parse_args()
    
    main(args)
