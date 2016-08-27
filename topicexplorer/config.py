# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 17:49:05 2016

@author: adi
"""
from vsm import *
from vsm.viewer.wrappers import doc_label_name

import os.path
from collections import defaultdict
from ConfigParser import ConfigParser as ConfigParser

# load the topic models
class keydefaultdict(defaultdict):
    """ Solution from: http://stackoverflow.com/a/2912455 """
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret
            
# load in the configuration file
class moduleLoad:
    
    def __init__(self,config_name):
        self.config_file = config_name
        #self.config_file = r"C:/Users/adi/Anaconda/topicexplorer/data23.ini" 
        self.config = ConfigParser({
            'topic_range': None,
            'topics': None})
        self.config.read(self.config_file)
        self.lda_m = keydefaultdict(self.load_model)
        self.lda_v = keydefaultdict(self.load_viewer)

    # load the corpus
    def load_corpus(self):
        self.c = Corpus.load(self.config.get('main', 'corpus_file'))
        self.context_type = self.config.get('main', 'context_type')
        self.ctx_metadata = self.c.view_metadata(self.context_type)
        self.all_ids = self.ctx_metadata[doc_label_name(self.context_type)]

    # create topic model patterns
    def create_model_pattern(self):
        self.pattern = self.config.get('main', 'model_pattern')
        if self.config.get('main', 'topics'):
            self.topic_range = eval(self.config.get('main', 'topics'))

    def load_model(self,k):
        if k in self.topic_range:
            return LdaCgsSeq.load(self.pattern.format(k))
        else:
            raise KeyError("No model trained for k={}.".format(k))
    def load_viewer(self,k):
        """ Function to dynamically load the LdaCgsViewer. 
            Failure handling for missing keys is handled by `load_model`"""
        return LdaCgsViewer(self.c,self.lda_m[k])

    