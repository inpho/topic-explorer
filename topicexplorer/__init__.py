from __future__ import absolute_import
from .version import __version__

from collections import defaultdict

from vsm import Corpus, LdaCgsSeq, LdaCgsViewer
from vsm.viewer.wrappers import doc_label_name

import topicexplorer.config

__all__ = ['__version__', 'from_config']

# load the topic models
class keydefaultdict(defaultdict):
    """ Solution from: http://stackoverflow.com/a/2912455 """
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret

def from_config(config_file):
    config = topicexplorer.config.read(config_file)

    # Load the corpus and metadata
    c = Corpus.load(config.get('main', 'corpus_file'))
    context_type = config.get('main', 'context_type')
    ctx_metadata = c.view_metadata(context_type)
    all_ids = ctx_metadata[doc_label_name(context_type)]

    # create topic model patterns
    pattern = config.get('main', 'model_pattern')
    if config.get('main', 'topic_range'):
        topic_range = list(map(int, config.get('main', 'topic_range').split(',')))
        topic_range = list(range(*topic_range))
    if config.get('main', 'topics'):
        topic_range = eval(config.get('main', 'topics'))

    # lazy load of models and viewers
    def load_model(k):
        if k in topic_range:
            return LdaCgsSeq.load(pattern.format(k))
        else:
            raise KeyError("No model trained for k={}.".format(k))
    def load_viewer(k):
        """ Function to dynamically load the LdaCgsViewer. 
            Failure handling for missing keys is handled by `load_model`"""
        return LdaCgsViewer(c,lda_m[k])

    lda_m = keydefaultdict(load_model)
    lda_v = keydefaultdict(load_viewer)

    return TopicExplorer(c, lda_v)

class TopicExplorer(object):
    def __init__(self, corpus, viewers):
        """
        :param corpus:
        :type vsm.Corpus:

        :param viewers:
        :type dict[int,LdaCgsViewer]:
        """

        self.corpus = corpus
        self._viewers = viewers

    def __getitem__(self, key):
        """ Returns a viewer. """
        return self._viewers[key]
