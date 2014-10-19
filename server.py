import csv
from datetime import datetime, timedelta
import json
import os.path
import re
from StringIO import StringIO

from vsm.corpus import Corpus
from vsm.model.beaglecomposite import BeagleComposite
from vsm.viewer.beagleviewer import BeagleViewer
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer

from bottle import request, response, route, run, static_file

def _cache_date(days=1):
    time = datetime.now() + timedelta(days=days)
    return time.strftime("%a, %d %b %Y %I:%M:%S GMT")

@route('/doc_topics/<doc_id>')
def doc_topic_csv(doc_id):
    response.content_type = 'text/csv; charset=UTF8'

    data = lda_v.doc_topics(doc_id)[0]

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['topic','prob'])
    writer.writerows([(t, "%6f" % p) for t,p in data])

    return output.getvalue()

@route('/docs/<doc_id>')
def doc_csv(doc_id, threshold=0.2):
    response.content_type = 'text/csv; charset=UTF8'

    data = lda_v.sim_doc_doc(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['doc','prob'])
    writer.writerows([(d, "%6f" % p) for d,p in data if p > threshold])

    return output.getvalue()

@route('/topics/<topic_no>.json')
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
    
    js = []
    for doc, prob in data:
        js.append({'doc' : doc, 'label': label(doc), 'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in lda_v.doc_topics(doc)[0]])})

    return json.dumps(js)

@route('/docs_topics/<doc_id>.json')
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
    
    js = []
    for doc, prob in data:
        js.append({'doc' : doc, 'label': label(doc), 'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in lda_v.doc_topics(doc)[0]])})

    return json.dumps(js)

@route('/topics.json')
def topics():
    response.content_type = 'application/json; charset=UTF8'
    response.set_header('Expires', _cache_date())

    data = lda_v.topics()

    js ={} 
    for i,topic in enumerate(data):
        for word, prob in topic[:10]:
            js.update({str(i) : dict([(w, p) for w,p in topic[:10]])})

    return json.dumps(js)

@route('/docs.json')
def docs():
    response.content_type = 'application/json; charset=UTF8'
    response.set_header('Expires', _cache_date())

    docs = lda_v.corpus.view_metadata(context_type)['document_label']
    js = list()
    for doc in docs:
        js.append({
            'id': doc,
            'label' : label(doc)
        })

    return json.dumps(js)

@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='www/')

@route('/')
def index():
    return send_static('index.html')



if __name__ == '__main__':
    from argparse import ArgumentParser
    from ConfigParser import ConfigParser
    import os.path
    def is_valid_filepath(parser, arg):
        if not os.path.exists(arg):
            parser.error("The file %s does not exist!" % arg)
        else:
            return arg

    parser = ArgumentParser()
    parser.add_argument('config', type=lambda x: is_valid_filepath(parser, x),
        help="Configuration file path")
    parser.add_argument('-k', type=int, required=True,
        help="Number of Topics")
    parser.add_argument('-p', dest='port', type=int, 
        help="Port Number", default=None)
    args = parser.parse_args()

    if args.port is None: 
        port = '18%03d' % args.k
    else:
        port = args.port

    # load in the configuration file
    config = ConfigParser()
    config.read(args.config)

    path = config.get('main', 'path')
    context_type = config.get('main', 'context_type')
    corpus_file = config.get('main', 'corpus_file')
    model_pattern = config.get('main', 'model_pattern') 

    lda_c = Corpus.load(corpus_file)
    lda_m = None
    lda_v = None
    def load_model(k):
        global lda_m, lda_v
        lda_m = LCM.load(model_pattern.format(k))
        lda_v = LDAViewer(lda_c, lda_m)

    load_model(args.k)
    label = lambda x: x

    run(host='0.0.0.0', port=port)

