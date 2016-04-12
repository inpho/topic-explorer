from collections import defaultdict
import json
import os.path
import numpy as np

from vsm.viewer.wrappers import doc_label_name, def_label_fn
from topicexplorer.lib.hathitrust import parse_marc, get_volume_from_marc

lda_v = None
metadata = None
context_type = None

class keydefaultdict(defaultdict):
    # http://stackoverflow.com/a/2912455
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret

ctx_md = keydefaultdict(lambda ctx: lda_v.corpus.view_metadata(ctx))

def init(viewer, config, args):
    global metadata
    global lda_v
    global context_type
    
    lda_v = viewer

    model_path = config.get('main', 'path')
    context_type = config.get('main', 'context_type')

    filename = os.path.join(model_path,'../metadata.json')
    print "Loading HTRC metadata from", filename

    with open(filename) as f:
        metadata = json.load(f)

def label(doc):
    if context_type == 'book':
        try:
            md = metadata[doc]
            return md['title'][0]
        except:
            return doc
    elif context_type == 'page':
        context_md = ctx_md['page']
        where = np.squeeze(np.where(np.in1d(context_md['page_label'], [doc])))
        page_no = context_md['file'][where]
        page_no = page_no.split('/')[-1]
        page_no = page_no.replace('.txt','')
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

def id_fn(md):
    context_md = lda_v.corpus.view_metadata(context_type)
    ctx_label = doc_label_name(context_type)
    return context_md[ctx_label] 
