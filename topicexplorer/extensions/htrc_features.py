from __future__ import absolute_import, print_function

import os.path
import subprocess
import tempfile

from progressbar import ProgressBar, Percentage, Bar
import concurrent.futures

from htrc_features.utils import download_file
from htrc_features import FeatureReader
from vsm.extensions.corpusbuilders import corpus_fromlist
from vsm.extensions.corpusbuilders.util import process_word, apply_stoplist 

def download_vols(ids, output_dir=None):
    # If no explicit output directory is specified, just create a temporary one
    if output_dir is None:
        output_dir = tempfile.mkdtemp()

    # Download extracted features
    paths = {id: '{}/{}.json.bz2'.format(output_dir, id) for id in ids}
    try:
        download_file(htids=ids, outdir=output_dir)
    except subprocess.CalledProcessError as e:
        missing = [id for id, p in paths.items() if not os.path.exists(p)]
        with open('error_missing.log', 'w') as outfile:
            outfile.write('\n'.join(missing))
        
        print("{} volume{} failed to download. "
              "See `error_missing.log`.".format(len(missing), 's' if len(missing) > 1 else ''))
        print("Continuing with volumes that succesfully downloaded...")
    
    paths = [p for id, p in paths.items() if os.path.exists(p)]
    return paths

def process_pages(vol):
    corpus = []
    for _, page in vol.tokenlist(section='body', case=False, pos=False).iteritems():
        tokens = [process_word(token[-1]) for token, count in page.iteritems() for i in range(count)]
        tokens = [t for t in tokens if t]
        if tokens:
            corpus.extend(tokens)

    return corpus


def create_corpus(ids, verbose=1):
    paths = download_vols(ids)
    filtered_ids = [os.path.basename(p).replace('.json.bz2','') for p in paths]

    if verbose:
        pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=len(ids))
        pbar = pbar.start()
        n = 0

    fr = FeatureReader(paths)
    corpus = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        vols = [executor.submit(process_pages, vol) 
                    for id_n, vol in enumerate(fr.volumes())]
        
        if verbose:
            for f in concurrent.futures.as_completed(vols):
                n += 1
                pbar.update(n)

        corpus = map(concurrent.futures.Future.result, vols)
        pbar.finish()
    corpus = list(corpus)
    
    c = corpus_fromlist(corpus, context_type='book')
    c = apply_stoplist(c, nltk_stop=True, freq=5)
    c.context_data[0]['book_label'] = filtered_ids

    return c
