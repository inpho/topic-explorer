from future import standard_library
standard_library.install_aliases()
import string

from bottle import static_file

import topicexplorer.config

raw_corpus_path = None
def init(app, config_file):
    global raw_corpus_path
    config = topicexplorer.config.read(config_file)

    raw_corpus_path = config.get('main', 'raw_corpus')

    @app.route('/fulltext/<doc_id>')
    def get_doc(doc_id):
        return static_file(doc_id, root=raw_corpus_path)


def label(doc):
    newdoc = doc.replace('_', ' ')
    newdoc = newdoc.replace('.txt', '')
    try:
        id, details = newdoc.split('--', 1)
        details = details.lower()
        id = id.replace("LETTER ", '')
        # newdoc = id + " -- " + string.capwords(details)
        newdoc = string.capwords(details)
    except:
        pass
    return newdoc
