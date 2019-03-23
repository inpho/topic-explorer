from typing import Iterable

import numpy as np

from vsm.viewer.ldacgsviewer import LdaCgsViewer
from vsm.spatial import KL_div

if __name__ != '__main__':
    import warnings
    warnings.warn("topicexplorer.analysis is a provisional extension. APIs change in a future release.", FutureWarning)


def text_to_text(tops: np.array=None, viewer: LdaCgsViewer=None, ids: Iterable[str]=None):
    """
    Performs a text-to-text analysis.

    Parameters
    ------------
    viewer: LdaCgsViewer
    ids: Iterable[str]
    tops: numpy.array
        pre-computed document_topic_matrix

    Returns
    ---------
    numpy.array
    """
    if tops is None:
        tops = viewer.doc_topic_matrix(ids)

    return np.array([KL_div(tops[t+1], tops[t])
                         for t in range(tops.shape[0]-1)])


def past_to_text(tops: np.array=None, viewer: LdaCgsViewer=None, ids: Iterable[str]=None):
    """
    Performs a past-to-text analysis.

    Must either pass `tops`, a pre-computed document-topic matrix, or both a `viewer` and `ids` object.

    Parameters
    ------------
    tops: numpy.array
        pre-computed document_topic_matrix
    viewer: LdaCgsViewer
    ids: Iterable[str]

    Returns
    ---------
    numpy.array
    """
    if tops is None:
        tops = viewer.doc_topic_matrix(ids)

    return np.array([KL_div(tops[t], tops[0:t].sum(axis=0) / t ) 
                         for t in range(1, tops.shape[0] -1)])


def novelty(viewer: LdaCgsViewer, id, ids, scale: int):
    """
    Barron et al. (2018) https://doi.org/10.1073/pnas.1717729115
    """
    tops = viewer.doc_topic_matrix(ids)
    idx = ids.index(id)

    return np.mean([KL_div(tops[idx], tops[idx-d]) for d in range(scale)])


def resonance(viewer: LdaCgsViewer, id, ids, scale: int):
    """
    Barron et al. (2018) https://doi.org/10.1073/pnas.1717729115
    """
    tops = viewer.doc_topic_matrix(ids)
    idx = ids.index(id)

    return np.mean([KL_div(tops[idx], tops[idx-d]) - KL_div(tops[idx], tops[idx+d]) for d in range(scale)])