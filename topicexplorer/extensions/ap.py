from ConfigParser import RawConfigParser as ConfigParser, NoOptionError
import os.path

from bottle import static_file

raw_corpus_path = None


def init(app, config_file):
    global raw_corpus_path
    config = ConfigParser({ 'raw_corpus' : 'ap/'  })
    config.read(config_file)

    raw_corpus_path = config.get('main', 'raw_corpus')

    @app.route('/fulltext/<doc_id>')
    def get_doc(doc_id):
        return static_file(doc_id, root=raw_corpus_path)


def label(doc):
    global raw_corpus_path

    path = os.path.join(raw_corpus_path, doc)
    if os.path.exists(path):
        with open(path) as docfile:
            docfile = docfile.read()
            return doc + ': ' + ' '.join(docfile.split()[:10]) + ' ...'
    else:
        return doc
