from HTMLParser import HTMLParser
import re

from inpho.corpus import sep

labels = sep.get_titles()
for id,label in labels.iteritems():
    label = re.sub("<.+>(.+)<\/.+>","\g<1>", label)
    labels[id] = HTMLParser().unescape(label)

def label(doc):
    return labels.get(doc, doc)
