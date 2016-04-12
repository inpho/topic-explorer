from collections import defaultdict
import json
import os.path
import numpy as np

from vsm.viewer.wrappers import doc_label_name, def_label_fn

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
    global lda_v
    global context_type
    
    lda_v = viewer
    context_type = config.get('main','context_type')

def label(doc):
    global ctx_md

    context_md = ctx_md['page']
    where = np.squeeze(np.where(np.in1d(context_md['page_label'], [str(doc)])))
    print where, context_md
    page_no = context_md[where]
    print where, page_no['title']
    return page_no['title']


def id_fn(md):
    context_md = lda_v.corpus.view_metadata(context_type)
    ctx_label = doc_label_name(context_type)
    return context_md[ctx_label] 
