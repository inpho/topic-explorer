import numpy as np

from vsm.viewer.ldacgsviewer import LdaCgsViewer
from vsm.spatial import KL_div

def past_to_text(viewer: LdaCgsViewer, ids):
    """
    Performs a past-to-text analysis.

    Parameters
    ------------
    viewer: LdaCgsViewer
    ids: List[str]

    Returns
    ---------
    numpy.array
    """
    tops = viewer.doc_topic_matrix(ids)
    return np.array([KL_div(tops[t], tops[0:t].sum(axis=0) / t ) 
                         for t in range(1, len(ids) -1)])

def text_to_text(viewer: LdaCgsViewer, ids):
    """
    Performs a text-to-text analysis.

    Parameters
    ------------
    viewer: LdaCgsViewer
    ids: List[str]

    Returns
    ---------
    numpy.array
    """
    tops = viewer.doc_topic_matrix(ids)
    return np.array([KL_div(tops[t+1], tops[t])
                         for t in range(len(ids) -1)])

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