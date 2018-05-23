# -*- coding: utf-8 -*-
from builtins import chr
import os

import platform
from topicexplorer.lib.util import get_static_resource_path 

chinese_punctuation = [
                       u'\xb7',
                       u'\u203b',
                       u'\u25a1',
                       u'\u25c7',
                       u'\u25cb',
                       u'\u25ce',
                       u'\u25cf',
                       u'\u3016',
                       u'\u3017',
                       u'\u25a1',
                       u'\uff3b',
                       u'\u2013',
                       u'\u2014',
                       u'\u2018',
                       u'\u2019',
                       u'\u201C',
                       u'\u201D',
                       u'\u2026',
                       u'\u3000',
                       u'\u3001',
                       u'\u3002',
                       u'\u3008',
                       u'\u3009',
                       u'\u300A',
                       u'\u300B',
                       u'\u300C',
                       u'\u300D',
                       u'\u300E',
                       u'\u300F',
                       u'\u3010',
                       u'\u3011',
                       u'\u3014',
                       u'\u3015',
                       u'\uFE50',
                       u'\uFF01',
                       u'\uFF08',
                       u'\uFF09',
                       u'\uFF0C',
                       u'\uFF0D',
                       u'\uFF0E',
                       u'\uFF10',
                       u'\uFF11',
                       u'\uFF12',
                       u'\uFF13',
                       u'\uFF14',
                       u'\uFF15',
                       u'\uFF16',
                       u'\uFF17',
                       u'\uFF18',
                       u'\uFF19',
                       u'\uFF1A',
                       u'\uFF1B',
                       u'\uFF1F',
                       u'\uFF3B',
                       u'\uFF3C',
                       u'\uFF3D',
                       u'\u250B']

import string 
for a in string.ascii_lowercase[:],string.ascii_uppercase[:],range(0,10):
    for b in a:        
        chinese_punctuation.append(str(b))

# escape ASCII in the chinese range
for n in range(32,91):
    chinese_punctuation.append(chr(n+65280))

chinese_punctuation.append('\n')
chinese_punctuation.append('\r')

import os.path
import topicexplorer.lib.mmseg as mmseg
modern_dic = mmseg.Dict(get_static_resource_path("mmseg/modern_words.dic"))
ancient_dic = mmseg.Dict(get_static_resource_path("mmseg/ancient_words.dic"))
chrs = mmseg.CharFreqs(get_static_resource_path("mmseg/chars.dic"))
ancient_mmseg = mmseg.MMSeg(ancient_dic, chrs)
modern_mmseg = mmseg.MMSeg(modern_dic, chrs)

def ancient_chinese_tokenizer(raw_text):
    tokens = []
    for token in ancient_mmseg.segment(raw_text):
        if token not in chinese_punctuation:
            tokens.append(token)

    return tokens

def modern_chinese_tokenizer(raw_text):
    tokens = []
    for token in mmseg.segment(raw_text):
        if token not in chinese_punctuation:
            tokens.append(token)

    return tokens
