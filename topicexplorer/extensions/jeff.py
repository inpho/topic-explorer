from bottle import route, static_file

@route('/fulltext/<doc_id>')
def get_doc(doc_id):
    return static_file(doc_id, root='/home/jammurdo/workspace/jefferson/corpus/')

import string
def label(doc):
    newdoc = doc.replace('_', ' ')
    newdoc = newdoc.replace('.txt','')
    try:
        id, details = newdoc.split('--',1)
        details = details.lower()
        id = id.replace("LETTER ",'')
        #newdoc = id + " -- " + string.capwords(details)
        newdoc = string.capwords(details)
    except:
        pass
    return newdoc


