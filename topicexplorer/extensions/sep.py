from future import standard_library
standard_library.install_aliases()

from configparser import ConfigParser
from html.parser import HTMLParser
import os.path
import re


def get_titles():
    """
    Returns a dictionary of { sep_dir : title } pairs.
    """
    config = ConfigParser()
    config.read('/var/inpho/inpho.ini')
    try:
        entries = os.path.join(config.get('corpus', 'db_path'), 'entries.txt')
    
        titles = {}
        with open(entries) as f:
            for line in f:
                sep_dir, title, rest = line.split('::', 2)
                title = title.replace(r"\'", "'")
                titles[sep_dir] = title

        return titles
    except:
        print("Failed to load SEP entires database.")
        return dict() # handled properly via default value in dict.get()


def init(app, config_file):
    global labels
    labels = get_titles()
    for id, label in labels.items():
        label = re.sub("<.+>(.+)<\/.+>","\g<1>", label)
        labels[id] = HTMLParser().unescape(label)


def label(doc):
    global labels

    # support for SEP Archive corpora
    if re.findall('\d{4}-', doc):
        sem_year, doc = doc.split('-',1)
        sem = sem_year[:-4]
        year = sem_year[-4:]

        # expand archive name
        if(sem == 'spr'):
            sem = "Spring"
        elif(sem == 'win'):
            sem = "Winter"
        elif(sem == 'sum'):
            sem = "Summer"
        elif(sem == 'fall'):
            sem = "Fall"

        return "{} [{} {}]".format(labels.get(doc, doc), sem, year)
    else:
        return labels.get(doc, doc)
