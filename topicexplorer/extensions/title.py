from vsm.viewer.wrappers import doc_label_name, def_label_fn
from collections import defaultdict

import numpy as np

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

def label(doc):
    context_md = lda_v.corpus.view_metadata(context_type)
    where = np.squeeze(np.where(np.in1d(context_md['article_label'], [doc])))
    return context_md['title'][where] 

