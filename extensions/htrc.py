import json

metadata = None
def init(model_path):
    global metadata
    filename = model_path + '../metadata.json'

    with open(filename) as f:
        metadata = json.load(f)

def label(doc):
    md = metadata[doc]
    return md['title'][0]
