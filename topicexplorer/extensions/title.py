from ConfigParser import RawConfigParser as ConfigParser, NoOptionError
from collections import defaultdict
import numpy as np

from vsm.viewer.wrappers import doc_label_name, def_label_fn

app = None
metadata = None
class keydefaultdict(defaultdict):
    # http://stackoverflow.com/a/2912455
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret

ctx_md = keydefaultdict(lambda ctx: app.c.view_metadata(ctx))

def init(_app, config_file):
    #viewer, config, args):
    global app, metadata
    app = _app

    config = ConfigParser()
    config.read(config_file)

    model_path = config.get('main', 'path')

def label(doc):
    context_md = app.c.view_metadata(app.context_type)
    where = np.squeeze(np.where(np.in1d(context_md['article_label'], [doc])))
    return context_md['title'][where] 

