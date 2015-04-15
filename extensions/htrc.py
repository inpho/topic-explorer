import json
import os.path

metadata = None
def init(model_path):
    global metadata
    filename = os.path.join(model_path,'../metadata.json')
    print "Loading HTRC metadata from", filename

    with open(filename) as f:
        metadata = json.load(f)

def label(doc):
    md = metadata[doc]
    return md['title'][0]
