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

@patch('topicexplorer.prep.input')
def test_get_high_filter(input_mock):
    input_mock.side_effect = ['3', 'y']
    high_filter, candidates = topicexplorer.prep.get_high_filter(corpus)
    assert high_filter == 3
    assert candidates == ['I']
    
    # Test selection of all words
    input_mock.side_effect = ['3', '1', '3', 'y']
    high_filter, candidates = topicexplorer.prep.get_high_filter(corpus)
    assert high_filter == 3
    assert candidates == ['I']
    
    # Test not accept
    input_mock.side_effect = ['3', 'n', '3', 'y']
    high_filter, candidates = topicexplorer.prep.get_high_filter(corpus)
    assert high_filter == 3
    assert candidates == ['I']

    # Test invalid action
    input_mock.side_effect = ['blahhhh', '3', 'y']
    high_filter, candidates = topicexplorer.prep.get_high_filter(corpus)
    assert high_filter == 3
    assert candidates == ['I']

@patch('topicexplorer.prep.input')
def test_get_low_filter(input_mock):
    input_mock.side_effect = ['1', 'y']
    low_filter, candidates = topicexplorer.prep.get_low_filter(corpus)
    assert low_filter == 1 
    assert all(w in candidates for w in ['came', 'saw', 'conquered'])
   
    # Test selection of all words
    input_mock.side_effect = ['1', '3', '1', 'y']
    low_filter, candidates = topicexplorer.prep.get_low_filter(corpus)
    assert low_filter == 1
    assert all(w in candidates for w in ['came', 'saw', 'conquered'])

    # Test not accept
    input_mock.side_effect = ['1', 'n', '1', 'y']
    low_filter, candidates = topicexplorer.prep.get_low_filter(corpus)
    assert low_filter == 1
    assert all(w in candidates for w in ['came', 'saw', 'conquered'])

    # Test invalid action
    input_mock.side_effect = ['blahhhh', '1', 'y']
    low_filter, candidates = topicexplorer.prep.get_low_filter(corpus)
    assert low_filter == 1
    assert all(w in candidates for w in ['came', 'saw', 'conquered'])
