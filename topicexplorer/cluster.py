# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 23:15:56 2016

@author: adi
"""
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import map
from builtins import range
from builtins import object

from codecs import open
from collections import defaultdict
from configparser import ConfigParser as ConfigParser
from itertools import repeat, chain
import os.path

import numpy as np
from sklearn import manifold
from sklearn import cluster
from vsm import *
from vsm.viewer.wrappers import doc_label_name



class dimensionReduce(object):
    def __init__(self,config_name):
        self.config_file = config_name        
        self.model = moduleLoad(self.config_file)
        self.model.load_corpus()
        self.model.create_model_pattern()
        self.topic_range = self.model.topic_range
        self.model_v = self.get_model_v()
        self.merge_word_topic = self.combine()
        self.isomap = None
        self.kmeans = None
        
    def get_model_v(self):
        temp_model_v={}
        for k in self.topic_range:
            temp_model_v[k]=self.model.load_viewer(k)
        return temp_model_v
    
    def combine(self):
        """
        Merges the topic-word matric from multiple topic models.
        """
        if len(self.topic_range) < 1:
            raise IndexError("No topic range")
        else:
            keys = list(self.model_v.keys())
            return np.vstack(self.model_v[keys[i]].phi.T 
                for i in np.argsort(keys))
            """
            temp_merge = self.model_v[sorted(self.model_v.keys())[0]].phi.T
            for i in range(1,len(self.topic_range)):
                temp_merge = np.vstack((temp_merge,self.model_v[sorted(self.model_v.keys())[i]].phi.T))
            return temp_merge
            """
    
    def fit_isomap(self):
        import math
        total_topics = self.merge_word_topic.shape[0]
        n_neighbors = int(min(3 * math.log(total_topics), .1 * total_topics))
        isomap_object = manifold.Isomap(n_neighbors=n_neighbors, n_components=2,
                                        eigen_solver='auto', tol=0, 
                                        max_iter=30000, path_method='auto', 
                                        neighbors_algorithm='auto')
        self.isomap = isomap_object.fit(self.merge_word_topic)
    
    def fit_kmeans(self,n_clusters):
        # Get the seed from the model to provide a consistent world
        # for kmeans clustering. Ensures determinism.
        keys = list(self.model_v.keys())
        try:
            # assume sequential
            seed = self.model_v[keys[0]].model.seed
        except AttributeError:
            # handle parallel if that's the case
            seed = self.model_v[keys[0]].model.seeds[0]
            
        self.no_clusters = n_clusters
        kmeans_object = cluster.KMeans(n_clusters, random_state=seed)
        self.kmeans = kmeans_object.fit(self.isomap.embedding_)

    def write(self,filename):
        ks = [repeat(k, k) for k in self.topic_range]
        ks = chain(*ks)
        topics = [range(k) for k in self.topic_range]
        topics = chain(*topics)

        with open(filename, 'w') as outfile:
            outfile.write('k,topic,orig_x,orig_y,cluster\n')
            for k, topic, isomap, label in zip(ks, topics, self.isomap.embedding_, self.kmeans.labels_):
                orig_x, orig_y = isomap
                row = [k, topic, orig_x, orig_y, label]
                row = ','.join(map(str, row)) + '\n'
                outfile.write(row)


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
class moduleLoad(object):
    
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

