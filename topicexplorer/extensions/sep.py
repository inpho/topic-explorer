from HTMLParser import HTMLParser
import re

def get_titles():
    """
    Returns a dictionary of { sep_dir : title } pairs.
    """
    entries = '/var/inphosemantics/SEPMirror/usr/encyclopedia/databases/entries.txt'
    
    titles = {}
    with open(entries) as f:
        for line in f:
            sep_dir, title, rest = line.split('::', 2)
            title = title.replace(r"\'", "'")
            titles[sep_dir] = title

    return titles


def init(app, config_file):
    global labels
    labels = get_titles()
    for id, label in labels.iteritems():
        label = re.sub("<.+>(.+)<\/.+>","\g<1>", label)
        labels[id] = HTMLParser().unescape(label)


def label(doc):
    global labels
    return labels.get(doc, doc)
