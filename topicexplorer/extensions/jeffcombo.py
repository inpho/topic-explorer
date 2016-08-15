from collections import defaultdict
from ConfigParser import RawConfigParser as ConfigParser, NoOptionError
import json
import os.path
import numpy as np
import string

from vsm.viewer.wrappers import doc_label_name, def_label_fn
from topicexplorer.lib.hathitrust import parse_marc, get_volume_from_marc
from bottle import route, static_file


@route('/fulltext/<doc_id>')
def get_doc(doc_id):
    return static_file(doc_id, root=os.path.abspath('TJCombo/'))
print "Loading TJCombo letters from:", os.path.abspath('TJCombo/')

metadata = None
app = None


class keydefaultdict(defaultdict):
    # http://stackoverflow.com/a/2912455

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret

ctx_md = keydefaultdict(lambda ctx: app.c.view_metadata(ctx))

def init(_app, config_file):
    global metadata
    global app
    app = _app

    config = ConfigParser()
    config.read(config_file)

    model_path = config.get('main', 'path')

    filename = os.path.join(model_path, '../metadata.json')
    print "Loading HTRC metadata from", filename

    with open(filename) as f:
        metadata = json.load(f)


def label(doc):
    if app.context_type == 'document' or app.context_type == 'article':
        doc = doc.replace('.txt', '')
        try:
            md = metadata[doc]
            return "BOOK -- " + md['title'][0]
        except:
            newdoc = doc.replace('_', ' ')
            try:
                id, details = newdoc.split('--', 1)
                details = details.lower()
                id = id.replace("LETTER ", '')
                # newdoc = id + " -- " + string.capwords(details)
                newdoc = string.capwords(details)
            except:
                pass
            return "LETTER -- " + newdoc
    elif app.context_type == 'page':
        context_md = ctx_md['page']
        where = np.squeeze(np.where(np.in1d(context_md['page_label'], [doc])))
        page_no = context_md['file'][where]
        page_no = page_no.split('/')[-1]
        page_no = page_no.replace('.txt', '')
        page_no = int(page_no)

        book_label = context_md['book_label'][where]
        md = metadata[book_label]
        try:
            xml = parse_marc(md['fullrecord'].encode('utf8'))
            vol = get_volume_from_marc(xml[0])
            return "p%s of %s of %s" % (page_no, vol, md['title'][0])
        except:
            pass
        try:
            return "p%s of %s" % (page_no, md['title'][0])
        except:
            return doc

