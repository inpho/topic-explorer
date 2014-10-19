import json

filename = ('/var/inphosemantics/data/20130101/htrc-anthropomorphism-1315/'
            'htrc-1315-metadata.json')

with open(filename) as f:
    metadata = json.load(f)

def label(doc):
    md = metadata[doc]
    return md[md.keys()[0]]['titles'][0]
