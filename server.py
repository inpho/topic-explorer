import csv
import json
from StringIO import StringIO

from vsm.corpus import Corpus
from vsm.model.beaglecomposite import BeagleComposite
from vsm.viewer.beagleviewer import BeagleViewer
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer

from bottle import request, response, route, run, static_file

path = '/var/inphosemantics/data/20140801/sep/vsm-data/'

lda_c = Corpus.load(path + 'sep-nltk-freq1.npz')
lda_m = None
lda_v = None
def load_model(k):
    global lda_m, lda_v
    lda_m = LCM.load(path + 'sep-nltk-freq1-article-LDA-K%s.npz' % k)
    lda_v = LDAViewer(lda_c, lda_m)



@route('/doc_topics/<sep_dir>')
def doc_topic_csv(sep_dir):
    sep_dir = sep_dir.lower()

    response.content_type = 'text/csv; charset=UTF8'

    doc_id = sep_dir + '.txt'
    data = lda_v.doc_topics(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['topic','prob'])
    writer.writerows([(t, "%6f" % p) for t,p in data])

    return output.getvalue()

@route('/docs/<sep_dir>')
def doc_csv(sep_dir, threshold=0.2):
    sep_dir = sep_dir.lower()

    response.content_type = 'text/csv; charset=UTF8'

    doc_id = sep_dir + '.txt'
    data = lda_v.sim_doc_doc(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['doc','prob'])
    writer.writerows([(d[:-4], "%6f" % p) for d,p in data if p > threshold and d != 'sample.txt'])

    return output.getvalue()

@route('/topics/<topic_no>.json')
def topic_csv(topic_no, N=40):
    response.content_type = 'application/json; charset=UTF8'

    data = lda_v.sim_top_doc([topic_no])[:N]
    js = []
    for doc, prob in data:
        if doc != 'sample.txt':
            js.append({'doc' : doc[:-4], 'prob' : prob,
                'topics' : dict([(t, p) for t,p in lda_v.doc_topics(doc)])})

    return json.dumps(js)

@route('/docs_topics/<sep_dir>.json')
def doc_topics(sep_dir, N=40):
    sep_dir = sep_dir.lower()
    try:
        N = int(request.query.n)
    except:
        pass

    response.content_type = 'application/json; charset=UTF8'

    doc_id = sep_dir + '.txt'
    if N > 0:
        data = lda_v.sim_doc_doc(doc_id)[:N]
    else:
        data = lda_v.sim_doc_doc(doc_id)[N:]
        data = reversed(data)

    js = []
    for doc, prob in data:
        if doc != 'sample.txt':
            js.append({'doc' : doc[:-4], 'prob' : prob,
                'topics' : dict([(t, p) for t,p in lda_v.doc_topics(doc)])})

    return json.dumps(js)

@route('/topics.json')
def topics():
    response.content_type = 'application/json; charset=UTF8'

    data = lda_v.topics()

    js ={} 
    for i,topic in enumerate(data):
        for word, prob in topic[:10]:
            js.update({str(i) : dict([(w, p) for w,p in topic[:10]])})

    return json.dumps(js)

@route('/docs.json')
def docs():
    response.content_type = 'application/json; charset=UTF8'

    data = lda_v.topics()
    js = [label[:-4] for label in lda_c.view_metadata('article')['article_label'] if label != 'sample.txt']

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
    args = parser.parse_args()

    port = '16%03d' % args.k

    load_model(args.k)
    run(host='inphodata.cogs.indiana.edu', port=port)

