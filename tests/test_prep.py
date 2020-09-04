from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import unittest2 as unittest

import sys
if sys.version_info.major == 2:
    from mock import Mock, patch, PropertyMock
elif sys.version_info.major == 3:
    from unittest.mock import Mock, patch, PropertyMock

import numpy as np

from vsm import Corpus
import topicexplorer.prep

text = ['I', 'came', 'I', 'saw', 'I', 'conquered']
ctx_data = [np.array([(2, 'Veni'), (4, 'Vidi'), (6, 'Vici')],
                    dtype=[('idx', '<i8'), ('sentence_label', '|S6')])]

corpus = Corpus(text, context_data=ctx_data, context_types=['sentence'])

def test_get_corpus_counts():
    items, counts = topicexplorer.prep.get_corpus_counts(corpus)
    assert all(items == [0,1,2,3])
    assert all(counts == [3,1,1,1])

def test_get_small_words():
    assert topicexplorer.prep.get_small_words(corpus, 2) == ['I']
    assert topicexplorer.prep.get_small_words(corpus, 1) == []

def test_get_closest_bin():
    assert topicexplorer.prep.get_closest_bin(corpus, 0) == 0 
    assert topicexplorer.prep.get_closest_bin(corpus, 0.2) == 1 
    assert topicexplorer.prep.get_closest_bin(corpus, 0.5) == 1 
    assert topicexplorer.prep.get_closest_bin(corpus, 0.7) == 3
    assert topicexplorer.prep.get_closest_bin(corpus, 0, reverse=True) == 4
    assert topicexplorer.prep.get_closest_bin(corpus, 0.2, reverse=True) == 3 
    assert topicexplorer.prep.get_closest_bin(corpus, 0.5, reverse=True) == 3 
    assert topicexplorer.prep.get_closest_bin(corpus, 0.7, reverse=True) == 1

def test_get_candidate_words():
    low_freq = topicexplorer.prep.get_closest_bin(corpus, 0.5)
    low_words = topicexplorer.prep.get_candidate_words(corpus, -low_freq)
    assert all(w in low_words for w in ['came', 'saw', 'conquered'])

    high_freq = topicexplorer.prep.get_closest_bin(corpus, 0.5, reverse=True)
    high_words = topicexplorer.prep.get_candidate_words(corpus, high_freq)
    assert all(w in high_words for w in ['I'])

    no_words = topicexplorer.prep.get_candidate_words(corpus, 0)
    assert no_words == []

    mask_words = topicexplorer.prep.get_candidate_words(
        corpus, -low_freq, words=low_words)
    assert len(mask_words) == 0

def test_get_high_filter():
    # Test with high filter of 3
    items, counts = topicexplorer.prep.get_corpus_counts(corpus)
    candidates, filtered = topicexplorer.prep.get_high_filter_stops(corpus, words=set(), items=items, counts=counts, num=3)
    assert len(corpus.words) - len(candidates) == 3
    assert candidates == ['I']
    
    # Test with high filter of 0
    candidates, filtered = topicexplorer.prep.get_high_filter_stops(corpus, words=set(), items=items, counts=counts, num=0)
    assert len(corpus.words) - len(candidates) == 4
    assert candidates == []

    # Test with high filter of 1, should return invalid
    t = unittest.TestCase('run')
    with t.assertRaises(ValueError):
        candidates, filtered = topicexplorer.prep.get_high_filter_stops(corpus, words=set(), items=items, counts=counts, num=1)
        assert len(corpus.words) - len(candidates) == 0
        assert candidates == ['I', 'came', 'conquered', 'saw']

    # Test with high filter of 100
    candidates, filtered = topicexplorer.prep.get_high_filter_stops(corpus, words=set(), items=items, counts=counts, num=100)
    assert len(corpus.words) - len(candidates) == 4
    assert candidates == []

def test_get_low_filter():
    # Test with low filter of 1
    items, counts = topicexplorer.prep.get_corpus_counts(corpus)
    candidates, filtered = topicexplorer.prep.get_low_filter_stops(corpus, words=set(), items=items, counts=counts, num=1)
    assert len(corpus.words) - len(candidates) == 1 
    assert all(w in candidates for w in ['came', 'saw', 'conquered'])
   
    # Test with low filter of 3
    t = unittest.TestCase('run')
    with t.assertRaises(ValueError):
        candidates, filtered = topicexplorer.prep.get_low_filter_stops(corpus, words=set(), items=items, counts=counts, num=3)
        assert len(corpus.words) - len(candidates) == 0
        assert all(w in candidates for w in ['came', 'saw', 'conquered', 'I'])  

    # Test with low filter of 0
    candidates, filtered = topicexplorer.prep.get_low_filter_stops(corpus, words=set(), items=items, counts=counts, num=0)
    assert len(corpus.words) - len(candidates) == 4
    assert all(w in candidates for w in [])

    # Test with low filter of 100
    with t.assertRaises(ValueError):
        candidates, filtered = topicexplorer.prep.get_low_filter_stops(corpus, words=set(), items=items, counts=counts, num=100)
        assert len(corpus.words) - len(candidates) == 0
        assert all(w in candidates for w in ['came', 'saw', 'conquered', 'I'])
