from bottle import route, static_file
import os.path
print os.path.abspath('ap')

@route('/fulltext/<doc_id>')
def get_doc(doc_id):
    return static_file(doc_id, root='ap')

import os.path
def label(doc):
    if os.path.exists('ap/'+doc):
        with open('ap/'+doc) as docfile:
            docfile = docfile.read()
            return doc + ': ' + ' '.join(docfile.split()[:10]) + ' ...'
    else:
        return doc
