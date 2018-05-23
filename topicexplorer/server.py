from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import str as text

from codecs import open
from configparser import RawConfigParser as ConfigParser, NoOptionError
import csv
from datetime import datetime, timedelta
from functools import partial
import hashlib
from importlib import import_module
from io import BytesIO,StringIO
import json
import itertools
import math
import os.path
from pkg_resources import resource_filename
import re
import socket
import sys
import threading
from urllib.parse import unquote
import webbrowser

from bottle import (abort, redirect, request, response, route, run, 
                    static_file, Bottle, ServerAdapter)
import topicexplorer.config
from topicexplorer.lib.color import get_topic_colors, rgb2hex
from topicexplorer.lib.ssl import SSLWSGIRefServer
from topicexplorer.lib.util import (int_prompt, bool_prompt, is_valid_filepath,
    is_valid_configfile, get_static_resource_path)

from vsm.corpus import Corpus
from vsm.model.lda import LDA
from vsm.viewer.ldacgsviewer import LdaCgsViewer as LDAViewer
from vsm.viewer.wrappers import doc_label_name

import random
import pystache

__all__ = ['populate_parser', 'main', '_set_acao_headers', 'Application']

token = ['default']

def _set_acao_headers(f):
    """
    Decorator to set Access-Control-Allow-Origin headers to enable cross-InPhO
    embedding of Topic Explorer bars.
    """
    def set_header(*args, **kwargs):
        host = request.get_header('Origin')
        if host and 'cogs.indiana.edu' in host: # pragma: no cover
            response.headers['Access-Control-Allow-Origin'] = host
        elif host and '127.0.0.1' in host: # pragma: no cover
            response.headers['Access-Control-Allow-Origin'] = host
        elif host and 'codepen.io' in host:
            response.headers['Access-Control-Allow-Origin'] = host
        elif host and 'inphoproject.org' in host:
            response.headers['Access-Control-Allow-Origin'] = host
        elif host and 'hypershelf.org' in host:
            response.headers['Access-Control-Allow-Origin'] = host
        return f(*args, **kwargs)
    return set_header

def _generate_etag(v):
    ''' Takes a model view and generates an etag using the v.phi and v.theta attributes '''
    # TODO: write a function using a hashlib digest
    x = hashlib.sha1()
    x.update(repr(v.phi).encode('utf-8'))
    x.update(repr(v.theta).encode('utf-8'))
    return x.hexdigest()

def _docs_etag(c):
    x = hashlib.sha1()
    x.update(repr(c).encode('utf-8'))
    return x.hexdigest()

def _cache_date(days=0, seconds=120):
    """
    Helper function to return the date for the cache header.
    """
    time = datetime.now() + timedelta(days=days, seconds=seconds)
    return time.strftime("%a, %d %b %Y %I:%M:%S GMT")


class Application(Bottle):
    """
    This is the primary Bottle application for the Topic Explorer.
    Each Application corresponds to a single Corpus object, but may
    have multiple LDA model objects.
    """

    def __init__(self, corpus_file='', model_pattern='', topic_range=None,
                 context_type='', label_module=None, config_file='',
                 fulltext=False, corpus_path='', tokenizer='default', **kwargs):
        super(Application, self).__init__()

        self.config_file = config_file

        # setup routes
        self.renderer = pystache.Renderer(escape=lambda u: u,
            string_encoding='utf8')
        self.icons = kwargs.get('icons', 'link')
        if fulltext:
            self._serve_fulltext(corpus_path)
        self._setup_routes(**kwargs)

        # load corpus
        self.context_type = context_type
        self.label_name = self.context_type + '_label'
        self._load_label_module(label_module, config_file)
        self._load_corpus(corpus_file)

        # load viewers
        self.v = dict()
        self.topic_range = topic_range
        self.colors = dict()
        self._load_viewers(model_pattern)

        token[0] = tokenizer

    def _load_label_module(self, label_module, config_file):
        try:
            label_module = import_module(label_module)
            print("imported label module")
            label_module.init(self, config_file)
        except (ImportError, NoOptionError, AttributeError):
            pass

        try:
            self.label = label_module.label
            print("imported label function")
        except (AttributeError, UnboundLocalError):
            self.label = lambda x: x
            print("using default label function")

        try:
            self.id_fn = label_module.id_fn
            print("imported id function")
        except (AttributeError, UnboundLocalError):
            self.id_fn = lambda metadata: metadata[self.label_name]
            print("using default id function")

    def _load_corpus(self, corpus_file):
        self.c = Corpus.load(corpus_file, load_corpus=False)
        self.labels = self.c.view_metadata(self.context_type)[self.label_name]

    def _load_viewers(self, model_pattern):
        self.id_fn = lambda md: md[self.label_name]
        for k in self.topic_range:
            m = LDA.load(model_pattern.format(k))
            self.v[k] = LDAViewer(self.c, m)
            self.colors[k] = dict(get_topic_colors(self.v[k]))
            self.v[k].dist_doc_doc = partial(
                self.v[k].dist_doc_doc, label_fn=self.id_fn)
            self.v[k].dist_top_doc = partial(
                self.v[k].dist_top_doc, label_fn=self.id_fn)

    def _setup_routes(self, **kwargs):
        @self.route('/<k:int>/doc_topics/<doc_id>')
        @_set_acao_headers
        def doc_topic_csv(k, doc_id):

            etag = _generate_etag(self.v[k])
            
            # Check for an "If-None-Match" tag in the header
            if request.get_header('If-None-Match', '') == etag:
                response.status = 304
                return "Not Modified"

            response.set_header("Etag", etag)
            #response.set_header('Cache-Control', 'max-age=120')
            
            if k not in self.topic_range:
                response.status = 400  # Not Found
                return "No model for k = {}".format(k)

            response.content_type = 'text/csv; charset=UTF8'

            try:
                data = self.v[k].doc_topics(doc_id)
            except KeyErrror:
                data = self.v[k].doc_topics(doc_id.decode('utf-8'))

            if sys.version_info[0] == 3:
                output = StringIO()
            else:
                output = BytesIO()

            writer = csv.writer(output)
            writer.writerow(['topic', 'prob'])
            writer.writerows([(t, "%6f" % p) for t, p in data])

            return output.getvalue()

        @self.route('/<k:int>/docs/<doc_id>')
        @_set_acao_headers
        def doc_csv(k, doc_id, threshold=0.2):
            etag = _generate_etag(self.v[k])

            if request.get_header('If-None-Match', '') == etag:
                response.status = 304
                return "Not Modified"

            if k not in self.topic_range:
                response.status = 400  # Not Found
                return "No model for k = {}".format(k)

            response.set_header('Etag', etag)
            response.content_type = 'text/csv; charset=UTF8'

            try:
                data = self.v[k].dist_doc_doc(doc_id)
            except KeyError:
                data = self.v[k].dist_doc_doc(doc_id.decode('utf-8'))

            if sys.version_info[0] == 3:
                output = StringIO()
            else:
                output = BytesIO()

            writer = csv.writer(output)
            writer.writerow(['doc', 'prob'])
            writer.writerows([(d, "%6f" % p) for d, p in data if p > threshold])

            return output.getvalue()

        @self.route('/<k:int>/topics/<topic_no:int>.json')
        @_set_acao_headers
        def topic_json(k, topic_no, N=40):
            
            etag = _generate_etag(self.v[k])
            
            #Check for an "If-None-Match" in the request
            if request.get_header('If-None-Match', '') == etag:
                response.status = 304
                return "Not Modified"

            if k not in self.topic_range:
                response.status = 400  # Not Found
                return "No model for k = {}".format(k)

            #response.set_header('Cache-Control', 'max-age=120')
            response.set_header('Etag', etag)

            response.content_type = 'application/json; charset=UTF8'
            try:
                N = int(request.query.n)
            except:
                pass

            if N > 0:
                data = self.v[k].dist_top_doc([topic_no])[:N]
            else:
                data = self.v[k].dist_top_doc([topic_no])[N:]
                data = reversed(data)

            docs = [doc for doc, prob in data]
            doc_topics_mat = self.v[k].doc_topics(docs)
            docs = self.get_docs(docs, id_as_key=True)

            js = []
            for doc_prob, topics in zip(data, doc_topics_mat):
                doc, prob = doc_prob
                struct = docs[doc]
                struct.update({'prob': float(1 - prob),
                               'topics': dict([(text(t), float(p)) for t, p in topics])})
                js.append(struct)

            return json.dumps(js)

        @self.route('/<k:int>/docs_topics/<doc_id:path>.json')
        @_set_acao_headers
        def doc_topics(k, doc_id, N=40):
            
            etag = _generate_etag(self.v[k])

            if request.get_header('If-None-Match', '') == etag:
                response.status = 304
                return "Not Modified"

            if k not in self.topic_range:
                response.status = 400  # Not Found
                return "No model for k = {}".format(k)

            try:
                N = int(request.query.n)
            except:
                pass

            response.set_header('Etag', etag)
            response.content_type = 'application/json; charset=UTF8'

            try:
                if N > 0:
                    data = self.v[k].dist_doc_doc(doc_id)[:N]
                else:
                    data = self.v[k].dist_doc_doc(doc_id)[N:]
                    data = reversed(data)
            except KeyError:
                doc_id = doc_id.decode('utf-8')
                if N > 0:
                    data = self.v[k].dist_doc_doc(doc_id)[:N]
                else:
                    data = self.v[k].dist_doc_doc(doc_id)[N:]
                    data = reversed(data)

            docs = [doc for doc, prob in data]
            doc_topics_mat = self.v[k].doc_topics(docs)
            docs = self.get_docs(docs, id_as_key=True)

            js = []
            for doc_prob, topics in zip(data, doc_topics_mat):
                doc, prob = doc_prob
                struct = docs[doc]
                struct.update({'prob': float(1 - prob),
                               'topics': dict([(text(t), float(p)) for t, p in topics])})
                js.append(struct)

            return json.dumps(js)

        @self.route('/<k:int>/word_docs.json')
        @_set_acao_headers
        def word_docs(k, N=40):
            import numpy as np

            etag = _generate_etag(self.v[k])
            
            # Check for an 'If-None-Match' tag  
            if request.get_header('If-None-Match', '') == etag:
                response.status = 304
                return "Not Modified"

            if k not in self.topic_range:
                response.status = 400  # Not Found
                return "No model for k = {}".format(k)

            try:
                N = int(request.query.n)
            except:
                pass

            try:
                query = request.query.q.lower()
                if self.c.words.dtype.type == np.string_:
                    query = query.encode('ascii', 'ignore')
                
                query = query.split('|')
            except:
                raise Exception('Must specify a query')

            response.set_header('Etag', etag)
            response.content_type = 'application/json; charset=UTF8'

            query = [word for word in query if word in self.c.words]

            # abort if there are no terms in the query
            if not query:
                response.status = 400  # Bad Request
                return "Search terms not in model"

            topics = self.v[k].dist_word_top(query, show_topics=False)
            data = self.v[k].dist_top_doc(topics['i'],
                                          weights=(topics['value'].max() - topics['value']))

            if N > 0:
                data = data[:N]
            else:
                data = data[N:]
                data = reversed(data)

            docs = [doc for doc, prob in data]
            doc_topics_mat = self.v[k].doc_topics(docs)
            docs = self.get_docs(docs, id_as_key=True)

            js = []
            for doc_prob, topics in zip(data, doc_topics_mat):
                doc, prob = doc_prob
                struct = docs[doc]
                struct.update({'prob': float(1 - prob),
                               'topics': dict([(text(t), float(p)) for t, p in topics])})
                js.append(struct)

            return json.dumps(js)

        @self.route('/<k:int>/topics.json')
        @_set_acao_headers
        def topics(k):
            from topicexplorer.lib.color import rgb2hex
            import numpy as np

            etag = _generate_etag(self.v[k])
            # Check if there is a "If-None-Match" ETag in the request
            if request.get_header('If-None-Match', '') == etag:
                response.status = 304
                return "Not Modified"

            if k not in self.topic_range:
                response.status = 400  # Not Found
                return "No model for k = {}".format(k)

            response.content_type = 'application/json; charset=UTF8'
            response.set_header('Expires', _cache_date())
            response.set_header('Cache-Control', 'max-age=120')
            response.set_header('ETag', etag)

            # set a parameter for number of words to return
            wordmax = 10  # for alphabetic languages
            if kwargs.get('lang', None) == 'cn':
                wordmax = 25  # for ideographic languages

            # populate word values
            phi = self.v[k].phi.T
            idxs = phi.argsort(axis=1)[:,::-1][:,:wordmax]
            # https://github.com/numpy/numpy/issues/4724
            idx_hack = np.arange(np.shape(phi)[0])[:,np.newaxis]

            dt = [('Word',self.c.words.dtype),('Prob',phi.dtype)]
            data = np.zeros(shape=(phi.shape[0], wordmax), dtype=dt)
            data['Word'] = self.c.words[idxs]
            data['Prob'] = phi[idx_hack, idxs]

            js = {}
            for i, topic in enumerate(data):
                js[text(i)] = {
                    "color": rgb2hex(self.colors[k][i]),
                    'words': dict([(text(w), float(p))
                                       for w, p in topic[:wordmax]])
                    }

            return json.dumps(js)

        @self.route('/topics.json')
        @_set_acao_headers
        def word_topic_distance():
            import numpy as np
            response.content_type = 'application/json; charset=UTF8'

            tokenizer = token[0]
            # parse query
            if tokenizer == 'default':
                from vsm.extensions.corpusbuilders.util import word_tokenize
                tokenizer = word_tokenize
            elif tokenizer == 'zh':
                from topicexplorer.lib.chinese import modern_chinese_tokenizer
                tokenizer = modern_chinese_tokenizer
            elif tokenizer == 'ltc' or tokenizer == 'och':
                from topicexplorer.lib.chinese import ancient_chinese_tokenizer
                tokenizer = ancient_chinese_tokenizer
            elif tokenizer == 'inpho':
                from topicexplorer.extensions.inpho import inpho_tokenizer
                tokenizer = inpho_tokenizer
            elif tokenizer == 'brain':
                from hyperbrain.parse import brain_tokenizer
                tokenizer = brain_tokenizer
            else:
                raise NotImplementedError(
                    "Tokenizer '{}' is not included in topicexplorer".format(tokenizer))

            query = list(itertools.chain(*[tokenizer(q) for q in request.query.q.split('|')]))

            stopped_words = [word for word in query 
                                 if word in self.c.stopped_words]
            query = [word for word in query if word in self.c.words]

            # abort if there are no terms in the query
            if not query and stopped_words:
                response.status = 410  # Gone
                return "Search terms removed using stoplist: " + ' '.join(query)
            elif not query:
                response.status = 404  # Not Found
                return "Search terms not in corpus"


            # calculate distances
            distances = dict()
            for k, viewer in self.v.items():
                d = viewer.dist_word_top(query, show_topics=False)
                distances[k] = np.fromiter(
                    ((k, row['i'], row['value']) for row in d),
                    dtype=[('k', '<i8'), ('i', '<i8'), ('value', '<f8')])

            # merge and sort all topics across all models
            merged_similarity = np.hstack(list(distances.values()))
            sorted_topics = merged_similarity[np.argsort(merged_similarity['value'])]

            # return data
            data = [{'k' : int(t['k']),
                     't' : int(t['i']),
                     'distance' : float(t['value']) } for t in sorted_topics]
            return json.dumps(data)


        @self.route('/topics')
        @_set_acao_headers
        def view_clusters():
            with open(get_static_resource_path('www/master.mustache.html'),
                      encoding='utf-8') as tmpl_file:
                template = tmpl_file.read()

            tmpl_params = {'body' : _render_template('cluster.mustache.html'),
                           'topic_range': self.topic_range}
            return self.renderer.render(template, tmpl_params)

        @self.route('/topics.local.html')
        @_set_acao_headers
        def view_clusters_local():
            with open(get_static_resource_path('www/master.local.mustache.html'),
                      encoding='utf-8') as tmpl_file:
                template = tmpl_file.read()

            tmpl_params = {'body' : _render_template('cluster.local.mustache.html'),
                           'topic_range': self.topic_range}
            return self.renderer.render(template, tmpl_params)


        @self.route('/docs.json')
        @_set_acao_headers
        def docs(docs=None, q=None, n=None):
            response.content_type = 'application/json; charset=UTF8'
            response.set_header('Expires', _cache_date())

            etag = _docs_etag(self.c)
            #Check for an "If-None-Match" tag in the header
            if request.get_header('If-None-Match', '') == etag:
              response.status=304
              return "Not Modified"

            response.set_header('Etag', etag)

            try:
                if request.query.q:
                    q = request.query.q
                    n = 10
            except:
                pass

            try:
                if request.query.id:
                    docs = [request.query.id]
            except:
                pass

            try:
                if request.query.random:
                    response.set_header('Expires', 0)
                    response.set_header('Pragma', 'no-cache')
                    response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    docs = [random.choice(self.labels)]
            except:
                pass

            js = self.get_docs(docs, query=q, n=n)

            return json.dumps(js)

        @self.route('/icons.js')
        def icons():
            with open(get_static_resource_path('www/icons.js')) as icons:
                text = '{0}\n var icons = {1};'\
                    .format(icons.read(), json.dumps(self.icons))
            return text

        def _render_template(page):
            response.set_header('Expires', _cache_date())

            with open(get_static_resource_path('www/' + page),
                      encoding='utf-8') as tmpl_file:
                template = tmpl_file.read()

            tmpl_params = {'corpus_name': kwargs.get('corpus_name', ''),
                           'corpus_link': kwargs.get('corpus_link', ''),
                           'context_type': self.context_type,
                           'topic_range': self.topic_range,
                           'doc_title_format': kwargs.get('doc_title_format', '{0}'),
                           'doc_url_format': kwargs.get('doc_url_format', ''),
                           'home_link': kwargs.get('home_link', '/')}
            return self.renderer.render(template, tmpl_params)

        @self.route('/<k:int>')
        def index_redirect(k):
            redirect('/{}/'.format(k))

        @self.route('/<k:int>/')
        def index(k):
            if k not in self.topic_range:
                abort(400, "No model for k = {}".format(k))

            with open(get_static_resource_path('www/master.mustache.html'),
                      encoding='utf-8') as tmpl_file:
                template = tmpl_file.read()

            tmpl_params = {'body' : _render_template('bars.mustache.html'),
                           'topic_range': self.topic_range}
            return self.renderer.render(template, tmpl_params)

        @self.route('/cluster.csv')
        @_set_acao_headers
        def cluster_csv(second=False):
            filename = kwargs.get('cluster_path')
            print("Retrieving cluster.csv:", filename)
            if not filename or not os.path.exists(filename):
                import topicexplorer.train
                filename = topicexplorer.train.cluster(10, self.config_file)
                kwargs['cluster_path'] = filename

            root, filename = os.path.split(filename)
            return static_file(filename, root=root)
        
        @self.route('/description.md')
        @_set_acao_headers
        def description():
            filename = kwargs.get('corpus_desc')
            if not filename:
                response.status = 404
                return "File not found"
            filename = get_static_resource_path(filename)
            root, filename = os.path.split(filename)
            return static_file(filename, root=root)
        
        @self.route('/')
        @_set_acao_headers
        def cluster():
            with open(get_static_resource_path('www/master.mustache.html'),
                      encoding='utf-8') as tmpl_file:
                template = tmpl_file.read()

            tmpl_params = {'body' : _render_template('splash.mustache.html'),
                           'topic_range': self.topic_range}
            return self.renderer.render(template, tmpl_params)

        @self.route('/<filename:path>')
        @_set_acao_headers
        def send_static(filename):
            return static_file(filename, root=get_static_resource_path('www/'))

    def _serve_fulltext(self, corpus_path):
        @self.route('/fulltext/<doc_id:path>')
        @_set_acao_headers
        def get_doc(doc_id):
            pdf_path = os.path.join(corpus_path, re.sub('txt$', 'pdf', doc_id))
            if os.path.exists(pdf_path.encode('utf-8')):
                doc_id = re.sub('txt$', 'pdf', doc_id)
            if os.path.exists(os.path.join(corpus_path, doc_id + '.txt')):
                doc_id = doc_id + '.txt'
            # here we deal with case where corpus_path and doc_id overlap
            (fdirs, lastdir) = os.path.split(corpus_path)
            if re.match('^' + lastdir, doc_id):
                return static_file(doc_id, root=fdirs)
            else:
                return static_file(doc_id, root=corpus_path)

    def get_docs(self, docs=None, id_as_key=False, query=None, n=None):
        ctx_md = self.c.view_metadata(self.context_type)

        if docs:
            # filter to metadata for selected docs
            ids = [self.c.meta_int(self.context_type, {self.label_name: doc}) for doc in docs]
            ctx_md = ctx_md[ids]
        else:
            # get metadata for all documents
            docs = self.labels

        js = dict() if id_as_key else list()

        def safe_text(s):
            try:
                return text(s)
            except:
                return ''

        for doc, md in zip(docs, ctx_md):
            if query is None or query.lower() in self.label(doc).lower():
                struct = {
                    'id': doc,
                    'label': self.label(doc),
                    # TODO: Figure out why metadata field might have issue.
                    'metadata': dict(zip(md.dtype.names, (safe_text(m) for m in md)))
                }

                if id_as_key:
                    js[doc] = struct
                else:
                    js.append(struct)
                if n is not None:
                    n = n-1
                    if n <= 0:
                        break


        return js


def get_host_port(args):
    """
    Returns the hostname and port number
    """
    config = ConfigParser({'port': '8000', 'host': '127.0.0.1'})
    with open(args.config, encoding='utf8') as configfile:
        config.read_file(configfile)

    # automatic port assignment
    def test_port(port):
        try:
            host = args.host or config.get("www", "host")
            if host == '0.0.0.0':
                host = 'localhost'
            try:
                s = socket.create_connection((host, port), 2)
                s.close()
                raise IOError("Socket connectable on port {0}".format(port))
            except socket.error:
                pass
            return port
        except IOError:
            if not args.quiet:
                port = int_prompt(
                    "Conflict on port {0}. Enter new port:".format(port))
                return test_port(port)
            else:
                raise IOError(
                    "Conflict on port {0}. Try running with -p to manually set new port.".format(port))

    port = args.port or int(config.get('www', 'port').format(0))
    port = test_port(port)

    # prompt to save
    if (int(config.get("www", "port").format(0))) != port:
        if not args.quiet and bool_prompt(
            "Change default baseport to {0}?".format(port), default=True):
            config.set("www", "port", text(port))

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
            config.read_file(config_string)

            # write deep copy without DEFAULT section
            # this preserves DEFAULT for rest of program
            with open(args.config, 'w') as configfh:
                new_config.write(configfh)

    # hostname assignment
    host = args.host or config.get('www', 'host')
    return host, port

class WaitressLoggingServer(ServerAdapter):
    def run(self, handler): # pragma: no cover
        from waitress import serve
        if not self.quiet:
            from paste.translogger import TransLogger
            handler = TransLogger(handler)
        serve(handler, host=self.host, port=self.port, **self.options)

def main(args, app=None):
    if app is None:
        app = create_app(args)

    host, port = get_host_port(args)

    if args.browser:

        if host == '0.0.0.0':
            link_host = "localhost"
        else:
            link_host = host
        url = "http://{host}:{port}/"
        url = url.format(host=link_host, port=port, k=min(app.topic_range))
        browser_thread = threading.Thread(target=webbrowser.open, args=[url])
        browser_thread.start()

        print("TIP: Browser launch can be disabled with the '--no-browser' argument:")
        print("topicexplorer serve --no-browser", args.config, "\n")

    app.run(server=WaitressLoggingServer, host=host, port=port)


def create_app(args):
    config = topicexplorer.config.read(args.config)

    # path variables
    context_type = config.get('main', 'context_type')
    corpus_file = config.get('main', 'corpus_file')
    model_pattern = config.get('main', 'model_pattern')
    cluster_path = config.get('main', 'cluster')

    # language customization
    lang = config.get('main', 'lang')

    # set topic_range
    if config.get('main', 'topics'):
        topic_range = eval(config.get('main', 'topics'))

    # get icons_list
    config_icons = config.get('www', 'icons').split(",")
    if args.fulltext or config.getboolean('www', 'fulltext'):
        if not any('fulltext' in icon for icon in config_icons) and 'ap' not in config_icons:
            # determines what fulltext function to use depending on the pdf tag that
            # was added in the init.py file
            if (config.getboolean('www', 'pdf')):
                config_icons.insert(0, 'fulltext-pdf')
            else:
                config_icons.insert(0, 'fulltext-inline')

    # Create application object
    corpus_name = config.get('www', 'corpus_name')
    corpus_link = config.get('www', 'corpus_link')
    doc_title_format = config.get('www', 'doc_title_format')
    doc_url_format = config.get('www', 'doc_url_format')
    home_link = config.get('www', 'home_link')
    label_module = config.get('main', 'label_module')
    corpus_path = config.get('main', 'raw_corpus')
    corpus_desc = config.get('main', 'corpus_desc')
    fulltext = args.fulltext or config.getboolean('www', 'fulltext')
    tokenizer = config.get('www', 'tokenizer')

    app = Application(corpus_file=corpus_file,
                      model_pattern=model_pattern,
                      topic_range=topic_range,
                      context_type=context_type,
                      label_module=label_module,
                      config_file=args.config,
                      corpus_path=corpus_path,
                      fulltext=fulltext,
                      lang=lang,
                      icons=config_icons,
                      corpus_name=corpus_name,
                      corpus_link=corpus_link,
                      doc_title_format=doc_title_format,
                      doc_url_format=doc_url_format,
                      cluster_path=cluster_path,
                      corpus_desc=corpus_desc,
                      home_link=home_link,
                      tokenizer=tokenizer)

    """
    host, port = get_host_port(args) 
    """
    # app.run(host='0.0.0.0', port=8081)
    return app


def populate_parser(parser):
    parser.add_argument('config', type=lambda x: is_valid_configfile(parser, x),
                        help="Configuration file path")
    parser.add_argument('-k', type=int, required=False,
                        help="Number of Topics")
    parser.add_argument('-p', dest='port', type=int,
                        help="Port Number", default=None)
    parser.add_argument('--host', default='127.0.0.1', help='Hostname')
    parser.add_argument('--no-browser', dest='browser', action='store_false')
    parser.add_argument("-q", "--quiet", action="store_true")
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
