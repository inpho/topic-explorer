# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 23:15:56 2016

@author: adi
"""

import config
from config import moduleLoad
import numpy as np
from sklearn import manifold
from sklearn import cluster
import os.path

class dimensionReduce:
    def __init__(self,config_name):
        self.config_file = config_name        
        #self.config_file = r"C:/Users/adi/Anaconda/topicexplorer/data23.ini"
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
        if len(self.topic_range) < 1:
            raise IndexError("no topic range")
        else:
            temp_merge = self.model_v[sorted(self.model_v.keys())[0]].phi.T
            for i in range(1,len(self.topic_range)):
                temp_merge = np.vstack((temp_merge,self.model_v[sorted(self.model_v.keys())[i]].phi.T))
            return temp_merge
    
    def fit_isomap(self):
        isomap_object = manifold.Isomap(n_neighbors=3, n_components=2, eigen_solver='auto', tol=0, max_iter=300, path_method='auto', neighbors_algorithm='auto')
        self.isomap = isomap_object.fit(self.merge_word_topic)
    
    def fit_kmeans(self,n_clusters):
        self.no_clusters = n_clusters
        kmeans_object = cluster.KMeans(n_clusters)
        self.kmeans = kmeans_object.fit(self.isomap.embedding_)
        
    def write_isomap(self,filename):
        if not os.path.isfile(filename +'_'+"isomapWWW.csv"):
            with open(filename +'_'+"isomapWWW.csv",'w') as isomap_file:
                isomap_file.write('x,y\n')
                for i in range(len(self.isomap.embedding_)):
                    isomap_file.write(str(self.isomap.embedding_[i][0])+','+str(self.isomap.embedding_[i][1])+'\n')
        
    def write_kmeans(self,filename):
        if not os.path.isfile(filename +'_'+"clusterWWW"+'_'+str(self.no_clusters)+".csv"):
            with open(filename +'_'+"clusterWWW"+'_'+str(self.no_clusters)+".csv",'w') as cluster_file:
                cluster_file.write('x,y\n')
                for i in range(len(self.kmeans.cluster_centers_ )):
                    cluster_file.write(str(self.kmeans.cluster_centers_[i][0])+','+str(self.kmeans.cluster_centers_[i][1])+'\n')
            
            with open(filename +'_'+"labelsWWW"+'_'+str(self.no_clusters)+".csv",'w') as label_file:
                label_file.write('x\n')
                for i in range(len(self.kmeans.labels_ )):
                    label_file.write(str(self.kmeans.labels_[i])+'\n')
        
    def write_topics(self,filename):
        if not os.path.isfile(filename +'_'+"topicsWWW.csv"):        
            with open(filename +'_'+"topicsWWW.csv",'w') as topic_file,open(filename +'_'+"topic_rangeWWW.csv",'w') as topicR_file:
                topic_file.write('topic\n')
                topicR_file.write('topic_range\n')
                for k in self.topic_range:
                    temp_model=self.model_v[k].topics()
                                    
                    for i in range(k):
                        temp_str = ''                    
                        for j in range(10):
                            temp_str=temp_str+' '+temp_model[i][j][0]
                        topic_file.write(temp_str+'\n')
                        topicR_file.write(str(k)+'\n')
            
        
    def write_model_file(self,filename):
        self.write_isomap(filename)
        self.write_kmeans(filename)
        self.write_topics(filename)