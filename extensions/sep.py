from inpho.corpus import sep

labels = sep.get_titles()
for id,label in labels.iteritems():
    label = re.sub("<.+>","", label)
    labels[id] = HTMLParser().unescape(label)

def label(doc):
    return labels.get(doc, doc)
