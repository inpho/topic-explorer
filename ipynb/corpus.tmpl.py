from vsm import *
from vsm.viewer.wrappers import doc_label_name

import os.path

# load in the configuration file
from ConfigParser import ConfigParser as ConfigParser
config_file = r"$config_file" 
config = ConfigParser({
        'topic_range': None,
        'topics': None})
config.read(config_file)

# load the corpus
c = Corpus.load(config.get('main', 'corpus_file'))
context_type = config.get('main', 'context_type')
ctx_metadata = c.view_metadata(context_type)
all_ids = ctx_metadata[doc_label_name(context_type)]

# create topic model patterns
pattern = config.get('main', 'model_pattern')
if config.get('main', 'topic_range'):
    topic_range = map(int, config.get('main', 'topic_range').split(','))
    topic_range = range(*topic_range)
if config.get('main', 'topics'):
    topic_range = eval(config.get('main', 'topics'))

# load the topic models
lda_m = dict()
lda_v = dict()
print topic_range
print pattern
for k in topic_range:
    lda_m[k] = LdaCgsSeq.load(pattern.format(k))
    lda_v[k] = LdaCgsViewer(c,lda_m[k])

## Colors
import itertools
import brewer2mpl as brewer

def brew(N, n_cls, reverse=True):
    b = [
        brewer.get_map('Blues', 'Sequential', N+1, reverse=reverse).mpl_colors[:N],
        brewer.get_map('Oranges', 'Sequential', N+1, reverse=reverse).mpl_colors[:N],
        brewer.get_map('Greens', 'Sequential', N+1, reverse=reverse).mpl_colors[:N],
        brewer.get_map('Purples', 'Sequential', N+1, reverse=reverse).mpl_colors[:N],
        brewer.get_map('Greys', 'Sequential', N+1, reverse=reverse).mpl_colors[:N],
        brewer.get_map('Reds', 'Sequential', N+1, reverse=reverse).mpl_colors[:N]
    ]
    return b[:n_cls]

def get_topic_colors(v):
    data = v.topic_oscillations()
    
    colors = [itertools.cycle(cs) for cs in zip(*brew(3,n_cls=4))]
    factor = len(data) / len(colors)
    
    topic_colors =  [(topic_datum[0], colors[min(rank / factor, len(colors)-1)].next()) 
                 for rank, topic_datum in enumerate(data)]
    topic_colors.sort(key=lambda x: x[0])
    return topic_colors

