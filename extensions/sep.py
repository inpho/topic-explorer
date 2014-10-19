from HTMLParser import HTMLParser
import re

from inpho.corpus import sep

labels = sep.get_titles()
for id,label in labels.iteritems():
    label = re.sub("<.+>","", label)
    labels[id] = HTMLParser().unescape(label)

def label(doc):
    doc = doc[:-4] # strip '.txt' extension
    return labels.get(doc, doc)
