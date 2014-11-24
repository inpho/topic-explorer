def _parse_ap():
    from StringIO import StringIO
    import xml.etree.ElementTree as ET
    print "parsing ap/ap.txt"
    with open('demo-data/ap/ap.txt') as f:
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

def label(doc):
    if plain_corpus.get(doc):
        return doc + ': ' + ' '.join(plain_corpus[doc].split()[:10]) + ' ...'
    else:
        return doc

from bottle import error, response, route
@route('/fulltext/<doc_id>')
def get_doc(doc_id):
    response.content_type = 'text/plain'
    try:
        return plain_corpus[doc_id]
    except KeyError:
        return error(404)
