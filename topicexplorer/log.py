"""
topicexplorer.lib.prov
Reading data from provenance graph. Eventually will facilitate replication of 
studies via provenance information.

This data schema will conform to the W3C's PROV-O specification, and reflects
the decisions of the PROV-DM description. The prefered rerpresentation is using
RDF Turtle 1.1.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime

from prov.model import ProvDocument, Identifier, Literal, PROV, Namespace, ProvActivity
from prov.dot import prov_to_dot

from collections import defaultdict
import topicexplorer

TE = Namespace('te', 'http://inphodata.cogs.indiana.edu/ontology#')
DCT = Namespace('dct', 'http://purl.org/dc/terms/')
PYPI = Namespace('pypi', 'http://pypi.python.org/pypi/topicexplorer/')
act = None
class TEProv(ProvDocument):
    def __init__(self):
        super(TEProv, self).__init__()
        self._convert()

    def _convert(self):
        self.set_default_namespace('http://example.org/')
        self.add_namespace('te', 'http://inphodata.cogs.indiana.edu/ontology#')
        mainte = self.entity(TE['topicexplorer'])
        mainte.add_asserted_type(PROV['Plan'])
        self.user = self.agent('user')
        #self.config = self.collection('config')
        self.corpus = self.entity('corpus', 
            other_attributes={PROV['label'] : 'workset'})
        #self.hadMember(self.config, self.corpus)
        self.models = {}
        self.modelRevisions = defaultdict(int)
        #self.corpus.wasDerivedFrom(Identifier("file:///some/local/path/"))
        self.lastRevision = 0
        self.lastAction = 0

    def add_command(self, cmd=None, activity_attributes=None, startTime=None, endTime=None):
        global act
        self.lastAction += 1

        act = self.activity('r{}act'.format(self.lastAction),
            startTime=startTime, endTime=endTime,
            other_attributes={PROV['label'] : 'topicexplorer {}'.format(cmd) })
        if self.lastAction > 1:
            act.wasInformedBy('r{}act'.format(self.lastAction -1))
        assoc = self.association(act, self.user, plan=TE['topicexplorer'])
        use = self.usage(act, entity=TE['topicexplorer'],
                other_attributes={DCT['hasVersion'] : PYPI[topicexplorer.__version__]})

        if cmd:
            act.add_asserted_type(TE[cmd])
        if activity_attributes:
            for key, val in activity_attributes.iteritems():
                if hasattr(val, '__iter__'):
                    for v in val:
                        act.add_attributes({TE[key] : v})
                else:
                    act.add_attributes({TE[key] : val})

        if cmd == 'init' or cmd == 'prep':
            self.lastRevision += 1
            if activity_attributes:
                new_rev = self.revise_corpus(name=activity_attributes.get('name'))
            else:
                new_rev = self.revise_corpus()
            
            if cmd == 'init':
                self.wasGeneratedBy(new_rev, activity=act)
            elif cmd == 'prep':
                new_rev.wasDerivedFrom('r{}'.format(self.lastRevision - 1),
                    activity=act, attributes={PROV['type'] : PROV['Revision']})

            # Invalidate past results if appropriate 
            prev = self.get_record('r{}act'.format(self.lastAction - 1))
            if prev and (PROV['type'], TE['train']) in prev[0].attributes:
                self.invalidation('r{}'.format(self.lastRevision - 1), activity=act)
                for k, model in self.models.iteritems():
                    self.invalidation(model, activity=act)
                    self.modelRevisions[k] += 1
                self.models = {}
                    
        elif cmd == 'train':
            for k in activity_attributes['k']:
                if k in self.models:
                    self.update_model(k, act)
                else:
                    new_model = self.add_model(k)
                    self.wasGeneratedBy(new_model, activity=act)
                    #new_model.wasDerivedFrom('r{}'.format(self.lastRevision), activity=act)
                    self.usage(act, 'r{}'.format(self.lastRevision))

            difference = set(self.models.keys()) - set(activity_attributes['k'])
            if difference:
                for k in difference:
                    self.invalidation(self.models[k], activity=act)
                    del self.models[k]

        return act


    def revise_corpus(self, name=''): 
        rev_num = 'r{}'.format(self.lastRevision)
        rev_label = name or rev_num
        new_rev = self.entity(rev_num, 
            other_attributes={PROV['label'] : rev_label})
        new_rev.specializationOf(self.corpus)
        new_rev.wasAttributedTo(self.user)
        new_rev.add_asserted_type(TE['Corpus'])
        return new_rev

    def update_model(self, k, act):
        self.modelRevisions[k] += 1
        new_model = self.entity('model{}r{}'.format(k, self.modelRevisions[k]))
        old_model = self.models[k]
        new_model.wasDerivedFrom(old_model, activity=act, 
            attributes={PROV['type'] : PROV['Revision']})
        new_model.add_asserted_type(TE['Model'])
        new_model.add_attributes({TE['k'] : k,
            PROV['label'] : 'k={} (r{})'.format(k, self.modelRevisions[k])})
        print('updating LABEL')
        new_model.wasAttributedTo(self.user)
        new_model.specializationOf('model{}'.format(k))

        self.models[k] = new_model

    def add_model(self, k):
        self.entity('model{}'.format(k), 
            other_attributes={PROV['label'] : 'k={}'.format(k)})
        new_model = self.entity('model{}r{}'.format(k, self.modelRevisions[k]))
        self.models[k] = new_model
        new_model.add_asserted_type(TE['Model'])
        new_model.add_attributes({TE['k'] : k,
            PROV['label'] : 'k={} (r{})'.format(k, self.modelRevisions[k])})
        new_model.wasAttributedTo(self.user)
        new_model.specializationOf('model{}'.format(k))
        #self.hadMember(self.config, 'model{}'.format(k))
        return new_model

    @staticmethod
    def deserialize(source=None, content=None, format='json', **args):
        raise NotImplementedError("deserialization not yet implemented.")
        doc = ProvDocument.deserialize(source, content, format, **args)
        doc.__class__ = TEProv        
        doc._convert()
        return doc

    @staticmethod
    def load(filename):
        import pickle
        with open(filename, 'rb') as provfile:
            doc = pickle.load(provfile)
        return doc

    def save(self, filename):
        import pickle
        with open(filename, 'wb') as provfile:
            pickle.dump(self, provfile)


a = TEProv()

a.add_command('init')
a.add_command('prep', {'highFilter' : 10000, 'lowFilter' : 10, 'lang' : 'en'})
a.add_command('train', {'k' : [10, 20, 40], 'iter' : 200, 'context-type': 'article'})
a.add_command('train', {'k' : [30, 20, 40], 'iter' : 200, 'context-type': 'article'})
a.add_command('prep', {'highFilter' : 5000, 'lowFilter' : 20})
a.add_command('train', {'k' : [30, 20, 40], 'iter' : 500, 'context-type': 'article'})
