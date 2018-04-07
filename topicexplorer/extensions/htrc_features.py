from __future__ import absolute_import, print_function
import sys
if sys.version_info[0] == 2:
    import backports.tempfile

from itertools import chain, repeat
import os.path
import pickle
import subprocess
import tempfile
import warnings

from progressbar import ProgressBar, Percentage, Bar
import concurrent.futures

from htrc_features.utils import download_file
from htrc_features import FeatureReader
from vsm.extensions.corpusbuilders import corpus_fromlist
from vsm.extensions.corpusbuilders.util import process_word, apply_stoplist 
from vsm.extensions.corpusbuilders.corpusstreamers import PickledWords

def download_vols(ids, output_dir=None):
    # If no explicit output directory is specified, just create a temporary one
    if output_dir is None:
        output_dir = tempfile.mkdtemp()

    # Download extracted features
    paths = {id: '{}/{}.json.bz2'.format(output_dir, id) for id in ids}
    try:
        download_file(htids=ids, outdir=output_dir)
    except subprocess.CalledProcessError:
        missing = [id for id, p in paths.items() if not os.path.exists(p)]
        with open('error_missing.log', 'w') as outfile:
            outfile.write('\n'.join(missing))
        
        print("{} volume{} failed to download. "
              "See `error_missing.log`.".format(len(missing), 's' if len(missing) > 1 else ''))
        print("Continuing with volumes that succesfully downloaded...")
    
    paths = [p for id, p in paths.items() if os.path.exists(p)]
    return paths

def process_pages(vol, pickle_dir=None):
    corpus = []
    for _, page in vol.tokenlist(section='body', case=False, pos=False).iteritems():
        tokens = chain.from_iterable(repeat(process_word(token[-1]), count) for token, count in page.iteritems())
        if tokens:
            corpus.extend(tokens)
    corpus = list(corpus)
    with tempfile.NamedTemporaryFile(delete=False, dir=pickle_dir) as fp:
        pickle.dump(corpus, fp)
        filename = fp.name
    del corpus

    return filename


def create_corpus(ids, nltk_stop=False, freq=0, verbose=1):
    paths = download_vols(ids)
    filtered_ids = [os.path.basename(p).replace('.json.bz2','') for p in paths]

    if verbose:
        pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=len(ids))
        pbar = pbar.start()
        n = 0

    if sys.version_info[0] == 2:
        TD = backports.tempfile.TemporaryDirectory 
    else:
        TD = tempfile.TemporaryDirectory
    with TD(prefix='vsm-') as pickle_dir:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')

            fr = FeatureReader(paths)
            corpus = []
            with concurrent.futures.ProcessPoolExecutor() as executor:
                vols = [executor.submit(process_pages, vol, pickle_dir) 
                            for id_n, vol in enumerate(fr.volumes())]
                
                if verbose:
                    for _ in concurrent.futures.as_completed(vols):
                        n += 1
                        pbar.update(n)

                pbar.finish()
                corpus_files = [vol.result() for vol in vols]

            corpus = [PickledWords(filename) for filename in corpus_files]
    
        c = corpus_fromlist(corpus, context_type='book')
        c = apply_stoplist(c, nltk_stop=nltk_stop, freq=freq)
        c.context_data[0]['book_label'] = filtered_ids

    return c
