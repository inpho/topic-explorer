import csv
import json
from StringIO import StringIO

from vsm.corpus import Corpus
from vsm.model.beaglecomposite import BeagleComposite
from vsm.viewer.beagleviewer import BeagleViewer
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer

from bottle import response, route, run, static_file

path = '/var/inphosemantics/data/20140801/sep/vsm-data/'

lda_c = Corpus.load(path + 'sep-nltk-freq1.npz')
lda_m = LCM.load(path + 'sep-nltk-freq1-article-LDA-K20.npz')
lda_v = LDAViewer(lda_c, lda_m)



@route('/doc_topics/<sep_dir>')
def doc_topic_csv(sep_dir):

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

    response.content_type = 'text/csv; charset=UTF8'

    doc_id = sep_dir + '.txt'
    data = lda_v.sim_doc_doc(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['doc','prob'])
    writer.writerows([(d[:-4], "%6f" % p) for d,p in data if p > threshold])

    return output.getvalue()

@route('/docs_topics/<sep_dir>.json')
def doc_topics(sep_dir, threshold=0.5):

    response.content_type = 'application/json; charset=UTF8'

    doc_id = sep_dir + '.txt'
    data = lda_v.sim_doc_doc(doc_id)

    js = []
    for doc, prob in data:
        if prob > threshold:
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


@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='www/')

@route('/')
def index():
    return send_static('index.html')

run(host='inphodata.cogs.indiana.edu', port='8888')

