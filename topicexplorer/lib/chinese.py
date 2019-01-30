# -*- coding: utf-8 -*-
import os

import platform
#updated to use pymmseg function calls instead of plain mmseg

import string
from topicexplorer.lib.util import get_static_resource_path

import os.path
import topicexplorer.lib.mmseg as mmseg
modern_dic = mmseg.Dict(get_static_resource_path("mmseg/modern_words.dic"))
ancient_dic = mmseg.Dict(get_static_resource_path("mmseg/ancient_words.dic"))
chrs = mmseg.CharFreqs(get_static_resource_path("mmseg/chars.dic"))
ancient_mmseg = mmseg.MMSeg(ancient_dic, chrs)
modern_mmseg = mmseg.MMSeg(modern_dic, chrs)

def is_flagged(toke_number):
             # '基本汉字'(Basic Chinese Character),20902 characters,'4E00-9FA5'
    return ((toke_number > ord(u'\u4E00') - 1 and toke_number < ord(u'\u9FEF') + 1) or \
            # '扩展A'(Expansion A),6582 characters,'3400-4DB5'
                (toke_number > ord(u'\u3400') - 1 and toke_number < ord(u'\u4DB5') + 1) or \
            # '扩展B'(Expansion B),42711 characters,'20000-2A6D6'
                (toke_number > int('20000', 16) - 1 and toke_number < int('2A6D6', 16) + 1) or \
            # '扩展C'(Expansion C),4149 characters,'2A700-2B734'
                (toke_number > int('2A700', 16) - 1 and toke_number < int('2B734', 16) + 1) or \
            # '扩展D'(Expansion D),222 characters,'2B740-2B81D'
                (toke_number > int('2B740', 16) - 1 and toke_number < int('2B81D', 16) + 1) or \
            # '扩展E'(Expansion E),5762 characters,'2B320-2CEA1'
                (toke_number > int('2B820', 16) - 1 and toke_number < int('2CEA1', 16) + 1) or \
            # '扩展F'(Expansion F),7473 characters,'2CEB0-2EBE0'
                (toke_number > int('2CEB0', 16) - 1 and toke_number < int('2EBE0', 16) + 1) or \
            # '康熙部首'(Kangxi Radical),214 characters,'2F00-2FD5'
                (toke_number > int('2F00', 16) - 1 and toke_number < int('2FD5', 16) + 1) or \
            # '部首扩展'(Radical Extension),115 characters,'2E80-2EF3'
                (toke_number > int('2E80', 16) - 1 and toke_number < int('2EF3', 16) + 1) or \
            # '兼容汉字'(Compatible Chinese characters),477 characters,'F900-FAD9'
                (toke_number > int('F900', 16) - 1 and toke_number < int('FAD9', 16) + 1) or \
            # '兼容扩展'(Compatible Extension),542 characters,'2F800-2FA1D'
                (toke_number > int('2F800', 16) - 1 and toke_number < int('2FA1D', 16) + 1) or \
            # 'PUA(GBK)部件'(PUA(GBK)Component),81 characters,'E815-E86F'
                (toke_number > int('E815', 16) - 1 and toke_number < int('E86F', 16) + 1) or \
            # '部件扩展'(Component Extension),452 characters,'E400-E5E8'
                (toke_number > int('E400', 16) - 1 and toke_number < int('E5E8', 16) + 1) or \
            # 'PUA增补'(PUA Supplement),207 characters,'E600-E6CF'
                (toke_number > int('E600', 16) - 1 and toke_number < int('E6CF', 16) + 1) or \
            # '汉字笔画'(Chinese Character Storks),36 characters,'31C0-31E3'
                (toke_number > int('31C0', 16) - 1 and toke_number < int('31E3', 16) + 1) or \
            # '汉字结构'(Chinese Character Structure),12 characters,'2FF0-2FFB'
                (toke_number > int('2FF0', 16) - 1 and toke_number < int('2FFB', 16) + 1) or \
            # '汉语注音'(Chinese Phonetic Notation),43 characters,'3105-312F'
                (toke_number > int('3105', 16) - 1 and toke_number < int('312F', 16) + 1) or \
            # '注音扩展'(Phonetic Notation Extension),22 characters,'31A0-31BA'
                (toke_number > int('31A0', 16) - 1 and toke_number < int('31BA', 16) + 1))

def ancient_chinese_tokenizer(raw_text):
    tokens = []
    for token in ancient_mmseg.segment(raw_text):
        flag = 1
        for toke in token:
            toke_number = ord(toke)
            if is_flagged(toke_number) == False:
                flag = 0
                break
        if flag:
            tokens.append(token)


    return tokens

def modern_chinese_tokenizer(raw_text):
    tokens = []
    for token in modern_mmseg.segment(raw_text):
        flag = 1
        for toke in token:
            toke_number = ord(toke)
            if is_flagged(toke_number) == False:
                flag = 0
                break
        if flag:
            tokens.append(token)

    return tokens
