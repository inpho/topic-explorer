import logging
import pickle
from typing import Iterable

import numpy as np
from vsm.viewer.ldacgsviewer import LdaCgsViewer

from topicexplorer import TopicExplorer
import topicexplorer.analysis

def text_to_text(te: TopicExplorer, k: int, ids: Iterable[str]=None,
                 nulls_ids: Iterable[Iterable[str]]=None) -> np.array:
    if ids is None:
        ids = te.corpus.ids
    v = te[k]

    idxs = [te.corpus.ids.index(id) for id in ids]
    logging.debug("Building topic matrix")
    tops = v.doc_topic_matrix(te.corpus.ids)

    logging.debug("Generating t2t and null_t2t")
    t2t = topicexplorer.analysis.text_to_text(tops[idxs])
    if nulls_ids:
        nulls_idx = [[te.corpus.ids.index(id) for id in null_ids] for null_ids in nulls_ids]
        null_t2t = np.array([topicexplorer.analysis.text_to_text(tops[null_idx]) for null_idx in nulls_idx])
        null_t2t = null_t2t.sum(axis=0) / len(null_t2t)

        return t2t - null_t2t

    else:
        return t2t

def past_to_text(te: TopicExplorer, k: int, ids: Iterable[str]=None,
                 nulls_ids: Iterable[Iterable[str]]=None) -> np.array:
    if ids is None:
        ids = te.corpus.ids

    logging.debug("Building topic matrix")
    tops = te[k].doc_topic_matrix(te.corpus.ids)
    idxs = [te.corpus.ids.index(id) for id in ids]

    logging.debug("Generating p2t and null_p2t")
    p2t = topicexplorer.analysis.past_to_text(tops[idxs])
    if nulls_ids:
        nulls_idx = [[te.corpus.ids.index(id) for id in null_ids] for null_ids in nulls_ids]
        null_p2t = np.array([topicexplorer.analysis.past_to_text(tops[null_idx]) for null_idx in nulls_idx])
        null_p2t = null_p2t.sum(axis=0) / len(null_p2t)

        return p2t - null_p2t

    else:
        return p2t

def load_null(filename: str):
    with open(filename, 'rb') as nullfile:
        null_ids = pickle.load(nullfile)
    
    return null_ids

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('config_file')
    parser.add_argument('null_file')
    parser.add_argument('-k', type=int)
    args = parser.parse_args()

    import topicexplorer
    te = topicexplorer.from_config(args.config_file)
    nulls_ids = load_null(args.null_file)
    t2t = text_to_text(te, args.k, nulls_ids=nulls_ids)
    p2t = past_to_text(te, args.k, nulls_ids=nulls_ids)

    import pylab
    pylab.plot(np.cumsum(t2t), label='text-to-text')
    pylab.plot(np.cumsum(p2t), label='past-to-text')
    pylab.legend()
    pylab.show()
