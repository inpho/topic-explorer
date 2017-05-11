from __future__ import absolute_import

import tempfile

from progressbar import ProgressBar, Percentage, Bar

from htrc_features.utils import download_file
from htrc_features import FeatureReader
from vsm.extensions.corpusbuilders import corpus_fromlist
from vsm.extensions.corpusbuilders.util import process_word, apply_stoplist 

def download_vols(ids, output_dir=None):
    # If no explicit output directory is specified, just create a temporary one
    if output_dir is None:
        output_dir = tempfile.mkdtemp()

    # Download extracted features
    download_file(htids=ids, outdir=output_dir)
    
    return map(lambda x: '{}/{}.json.bz2'.format(output_dir, x), ids)

def create_corpus(ids, verbose=1):
    paths = download_vols(ids)

    if verbose:
        pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=len(ids))
        pbar = pbar.start()

    fr = FeatureReader(paths)
    corpus = []
    for id_n, vol in enumerate(fr.volumes()):
        for _, page in vol.tokenlist(section='body', case=False, pos=False).iteritems():
            tokens = [process_word(token[-1]) for token, count in page.iteritems() for i in range(count)]
            tokens = [t for t in tokens if t]
            if tokens:
                corpus.append(tokens)
        pbar.update(id_n+1)

    c = corpus_fromlist(corpus, context_type='book')
    c = apply_stoplist(c, nltk_stop=True, freq=5)
    c.context_data[0]['book_label'] = ids

    return c
