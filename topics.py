import csv
from StringIO import StringIO

from vsm.corpus import Corpus
from vsm.model.beaglecomposite import BeagleComposite
from vsm.viewer.beagleviewer import BeagleViewer
from vsm.model.ldacgsmulti import LdaCgsMulti as LCM
from vsm.viewer.ldagibbsviewer import LDAGibbsViewer as LDAViewer

from bottle import response, route, run, static_file

path = '/media/Media/inphosemantics/'

lda_c = Corpus.load(path + 'sep-nltk-freq1.npz')
lda_m = LCM.load(path + 'sep-nltk-freq1-LdaCgsMulti-K140-2000-chain2.model.npz')
lda_v = LDAViewer(lda_c, lda_m)

@route('/topics/<sep_dir>')
def topic_csv(sep_dir):

    response.content_type = 'text/csv; charset=UTF8'

    doc_id = sep_dir + '.txt'
    data = lda_v.doc_topics(doc_id)

    output=StringIO()
    writer = csv.writer(output)
    writer.writerow(['topic','prob'])
    writer.writerows([(t, "%6f" % p) for t,p in data])

    return output.getvalue()


@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='www/')

@route('/')
def index():
    return send_static('index.html')

run(host='localhost', port='8080')

