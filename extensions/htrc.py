import json
import os.path
import numpy as np

from vsm.viewer.wrappers import doc_label_name, def_label_fn

lda_v = None
metadata = None
context_type = None
def init(model_path, viewer, ctx_type):
    global metadata
    global lda_v
    global context_type
    filename = os.path.join(model_path,'../metadata.json')
    print "Loading HTRC metadata from", filename

    with open(filename) as f:
        metadata = json.load(f)
    
    lda_v = viewer
    context_type = ctx_type

def label(doc):
    if context_type == 'book':
        md = metadata[doc]
        return md['title'][0]
    elif context_type == 'page':
        context_md = lda_v.corpus.view_metadata('page')
        where = np.squeeze(np.where(np.in1d(context_md['page_label'], [doc])))
        page_no = context_md[where]['file']
        page_no = page_no.split('/')[-1]
        page_no = page_no.replace('.txt','')
        page_no = int(page_no)

        book_label = context_md[where]['book_label']
        md = metadata[book_label]
        return "p%s of %s" % (page_no, md['title'][0])

def id_fn(md):
    context_md = lda_v.corpus.view_metadata(context_type)
    ctx_label = doc_label_name(context_type)
    return context_md[ctx_label] 
