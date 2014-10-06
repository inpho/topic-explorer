import csv
from datetime import datetime, timedelta
import json
from StringIO import StringIO

from vsm.corpus import Corpus
from vsm.model.beaglecomposite import BeagleComposite
from vsm.viewer.beagleviewer import BeagleViewer
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer

from bottle import request, response, route, run, static_file

path ='demo-data/'
context_type = 'document'
lda_c = Corpus.load(path + 'ap.npz')
lda_m = None
lda_v = None
def load_model(k):
    global lda_m, lda_v
    lda_m = LCM.load(path + 'models/ap89-K%d.npz' % k)
    lda_v = LDAViewer(lda_c, lda_m)

def _cache_date(days=1):
    time = datetime.now() + timedelta(days=days)
    return time.strftime("%a, %d %b %Y %I:%M:%S GMT")

@route('/doc_topics/<doc_id>')
def doc_topic_csv(doc_id):
    response.content_type = 'text/csv; charset=UTF8'

    data = lda_v.doc_topics(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['topic','prob'])
    writer.writerows([(t, "%6f" % p) for t,p in data])

    return output.getvalue()

def _parse_ap():
    from StringIO import StringIO
    import xml.etree.ElementTree as ET
    print "parsing ap/ap.txt"
    with open(path+ 'ap/ap.txt') as f:
        ap89_plain = f.read()
    
    ap89_plain = '<DOCS>\n' + ap89_plain + '</DOCS>\n'
    ap89_plain = ap89_plain.replace('&', '&#038;')
    ap89_IO = StringIO(ap89_plain)
    tree = ET.parse(ap89_IO)
    docs = tree.getroot()
    
    corpus = dict()
    for doc in docs:
        docno = doc.find('DOCNO').text.strip()
        text = doc.find('TEXT').text.strip().replace('&#038;', '&')
        corpus[docno] = text

    return corpus

plain_corpus = _parse_ap()

@route('/docs/<doc_id>.txt')
def get_doc(doc_id):
    response.content_type = 'text/plain'
    return plain_corpus[doc_id]

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
        js.append({'doc' : doc, 'label': doc, 'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in lda_v.doc_topics(doc)])})

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
        js.append({'doc' : doc, 'label': doc, 'prob' : 1-prob,
            'topics' : dict([(str(t), p) for t,p in lda_v.doc_topics(doc)])})

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

    docs = lda_c.view_metadata(context_type)['document_label']
    js = list()
    for doc in docs:
        js.append({
            'id': doc,
            'label' : doc
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
    parser = ArgumentParser()
    parser.add_argument('k', type=int)
    parser.add_argument('-p', dest='port', type=int, 
        help="Port Number", default=None)
    args = parser.parse_args()

    if args.port is None: 
        port = '16%03d' % args.k
    else:
        port = args.port

    load_model(args.k)
    run(host='0.0.0.0', port=port)

