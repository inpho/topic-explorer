from bottle import route, static_file

@route('/fulltext/<doc_id>')
def get_doc(doc_id):
    return static_file(doc_id, root='demo-data/ap/')

import os.path
def label(doc):
    if os.path.exists('demo-data/ap/'+doc):
        with open('demo-data/ap/'+doc) as docfile:
            docfile = docfile.read()
            return doc + ': ' + ' '.join(docfile.split()[:10]) + ' ...'
    else:
        return doc
