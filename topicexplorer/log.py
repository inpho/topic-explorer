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

import topicexplorer

TE = Namespace('te', 'http://inphodata.cogs.indiana.edu/ontology#')
DCT = Namespace('dct', 'http://purl.org/dc/terms/')
PYPI = Namespace('pypi', 'http://pypi.python.org/pypi/topicexplorer/')
act = None
class TEProv(ProvDocument):
    def __init__(self):
        super(TEProv, self).__init__()
        self.set_default_namespace('http://example.org/')
        self.add_namespace('te', 'http://inphodata.cogs.indiana.edu/ontology#')
        self.user = self.agent('user')
        self.corpus = self.entity('corpus')
        #self.corpus.wasDerivedFrom(Identifier("file:///some/local/path/"))
        self.lastRevision = 0

    def add_command(self, cmd=None, activity_attributes=None):
        global act
        self.lastRevision += 1
        new_rev = self.entity('r{}'.format(self.lastRevision))
        new_rev.specializationOf(self.corpus)
        new_rev.wasAttributedTo(self.user)

        act = self.activity('r{}act'.format(self.lastRevision),
            startTime=datetime.now(), endTime=datetime.now())
        if cmd:
            act.add_asserted_type(TE[cmd])
        if activity_attributes:
            for key, val in activity_attributes.iteritems():
                if hasattr(val, '__iter__'):
                    for v in val:
                        act.add_attributes({TE[key] : v})
                else:
                    act.add_attributes({TE[key] : val})

        assoc = self.association(act, self.user, plan=TE['topicexplorer'])
        use = self.usage(act, entity=TE['topicexplorer'],
                other_attributes={DCT['hasVersion'] : PYPI[topicexplorer.__version__]})
        if self.lastRevision == 1:
            self.wasGeneratedBy(new_rev, activity=act)
        else:
            new_rev.wasDerivedFrom('r{}'.format(self.lastRevision - 1),
                activity=act, attributes={'prov:type' : PROV['Revision']})


a = TEProv()
a.add_command('init')
a.add_command('prep', {'highFilter' : 10000, 'lowFilter' : 10, 'lang' : 'en'})
a.add_command('prep', {'highFilter' : 8000})
a.add_command('train', {'k' : [10, 20, 40], 'iter' : 200, 'context-type': 'article'})
print(a.serialize(None, 'xml'))
