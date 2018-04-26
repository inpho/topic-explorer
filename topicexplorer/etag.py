from corpus import *
import hashlib

def generate_etag(v):
    ''' Takes a model view and generates an etag using the v.phi and v.theta attributes '''
    # TODO: write a function using a hashlib digest
    x = hashlib.sha1()
    x.update(repr(v.phi).encode('utf-8'))
    x.update(repr(v.theta).encode('utf-8'))
    return x.hexdigest()


print(generate_etag(lda_v[20]))
print(generate_etag(lda_v[40]))
