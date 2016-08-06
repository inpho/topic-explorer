from collections import defaultdict
import json
import os.path
import numpy as np

from vsm.viewer.wrappers import doc_label_name, def_label_fn

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
    global app
    app = _app

def label(doc):
    global ctx_md

    context_md = ctx_md['page']
    where = np.squeeze(np.where(np.in1d(context_md['page_label'], [str(doc)])))
    if where:
        title = np.array(context_md[where])['title']
        return str(title)
    else:
        return doc

