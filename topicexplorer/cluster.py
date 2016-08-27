# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 23:15:56 2016

@author: adi
"""

from codecs import open
import config
from config import moduleLoad
import numpy as np
from sklearn import manifold
from sklearn import cluster
import os.path
from itertools import repeat, chain, izip

class dimensionReduce:
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
            keys = self.model_v.keys()
            return np.vstack(self.model_v[keys[i]].phi.T 
                for i in np.argsort(keys))
            """
            temp_merge = self.model_v[sorted(self.model_v.keys())[0]].phi.T
            for i in range(1,len(self.topic_range)):
                temp_merge = np.vstack((temp_merge,self.model_v[sorted(self.model_v.keys())[i]].phi.T))
            return temp_merge
            """
    
    def fit_isomap(self):
        isomap_object = manifold.Isomap(n_neighbors=3, n_components=2, eigen_solver='auto', tol=0, max_iter=300, path_method='auto', neighbors_algorithm='auto')
        self.isomap = isomap_object.fit(self.merge_word_topic)
    
    def fit_kmeans(self,n_clusters):
        # Get the seed from the model to provide a consistent world
        # for kmeans clustering. Ensures determinism.
        keys = self.model_v.keys()
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
        topics = [xrange(k) for k in self.topic_range]
        topics = chain(*topics)

        with open(filename, 'w') as outfile:
            outfile.write('k,topic,orig_x,orig_y,cluster\n')
            for k, topic, isomap, label in zip(ks, topics, self.isomap.embedding_, self.kmeans.labels_):
                orig_x, orig_y = isomap
                row = [k, topic, orig_x, orig_y, label]
                row = ','.join(map(str, row)) + '\n'
                outfile.write(row)


