from collections import defaultdict
from typing import Any, Dict, Iterable, List

import numpy as np

from vsm.spatial import KL_div
from vsm.viewer.ldacgsviewer import LdaCgsViewer

def population_text_to_text(v: LdaCgsViewer, population: List[str], dates: Iterable):
    # get the topics for the population
    topics = v.doc_topic_matrix(population)

    # build dictionary of ids at each date
    ids_at_date = defaultdict(list) # type: Dict[Any, List[str]]
    for id, date in zip(population, dates):
        ids_at_date[date].append(id)

    # calculate averages for all pairs from one date to the next
    t2t = []
    date_keys = sorted(ids_at_date.keys())
    for i in range(len(date_keys)-1):
        potential_jumps = ids_at_date[date_keys[i]][:]
        potential_jumps.extend(ids_at_date[date_keys[i+1]])
        KLs = []
        for id1 in ids_at_date[date_keys[i]]:
            for id2 in potential_jumps:
                if id1 != id2:
                    KLs.append(KL_div(topics[population.index(id2)], topics[population.index(id1)]))
        
        
        avg = np.average(KLs)
        for i in range(len(ids_at_date[date_keys[i]])):
            t2t.append(avg)

    return t2t

def population_past_to_text(v: LdaCgsViewer, population: List[str], dates: Iterable):
    # get the topics for the population
    topics = v.doc_topic_matrix(population)

    # build dictionary of ids at each date
    ids_at_date = defaultdict(list) # type: Dict[Any, List[str]]
    for id, date in zip(population, dates):
        ids_at_date[date].append(id)

    # calculate the averages for all possible past-to-text-orderings
    p2t = []    
    for i in range(len(date_keys)-1):
        prev = sum(len(ids_at_date[t]) for t in date_keys[:i+1])

        potential_jumps = ids_at_date[date_keys[i]][:]
        potential_jumps.extend(ids_at_date[date_keys[i+1]])
        KLs = []

        for id1 in ids_at_date[date_keys[i]]:
            for id2 in potential_jumps:
                if id1 != id2:
                    KLs.append(KL_div(topics[population.index(id1)], topics[0:prev].sum(axis=0)/prev))
        
        
        avg = np.average(KLs)
        for i in range(len(ids_at_date[date_keys[i]])):
            p2t.append(avg)

    return p2t
