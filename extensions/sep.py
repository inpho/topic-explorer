from HTMLParser import HTMLParser
import re

from inpho.corpus import sep

labels = sep.get_titles()
for id,label in labels.iteritems():
    label = re.sub("<.+>(.+)<\/.+>","\g<1>", label)
    labels[id] = HTMLParser().unescape(label)

def label(doc):
    
    doc = doc.split('-',1);
    print doc
    sem = str(doc[0])
    match = re.match(r"([a-z]+)([0-9]+)",sem, re.I)
    if match:
    	items = match.groups()
	print items
    year = items[1]
    sem = items[0]
    if(sem == 'spr'):
	sem = "Spring"
    if(sem == 'win'):
        sem = "Winter"
    if(sem == 'sum'):
        sem = "Summer"
    if(sem == 'fall'):
        sem = "Fall"
    
    topic = doc[1] 
    topic = str(topic.split('.')[0])
    topic = labels.get(topic, topic)
    return topic+' ['+sem+' '+year+'] '
