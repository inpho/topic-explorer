import json
from time import sleep
from urllib2 import urlopen
from urllib import quote_plus

def metadata(id, sleep_time=1):
    solr ="http://chinkapin.pti.indiana.edu:9994/solr/meta/select/?q=id:%s" % id
    solr += "&wt=json" ## retrieve JSON results
    # TODO: exception handling
    if sleep_time:
        sleep(sleep_time) ## JUST TO MAKE SURE WE ARE THROTTLED
    try:
        data = json.load(urlopen(solr))
        print id
        return data['response']['docs'][0]
    except ValueError :
        print "No result found for " + id 
        return dict()

import os.path,os
import sys
ids = os.listdir(sys.argv[-1])
print ids
data = [(id.strip(), metadata(id.strip())) for id in ids]
print data
data = dict(data)
with open(os.path.join(sys.argv[-1], '../metadata.json'),'wb') as outfile:
    json.dump(data, outfile)
    
