#!/usr/bin/python 
# -*- encoding: UTF-8 -*-
# http://yongsun.me/2013/06/simple-implementation-of-mmseg-with-python/

import codecs
import sys
from math import log
from collections import defaultdict

class Trie (object):
    class TrieNode:
        def __init__ (self):
            self.val = 0
            self.trans = {}

    def __init__ (self):
        self.root = Trie.TrieNode()

    def __walk (self, trienode, ch):
        if ch in trienode.trans:
            trienode = trienode.trans[ch]
            return trienode, trienode.val
        else:
            return None, 0

    def add (self, word, value=1):
        curr_node = self.root
        for ch in word:
            try: 
                curr_node = curr_node.trans[ch]
            except:
                curr_node.trans[ch] = Trie.TrieNode()
                curr_node = curr_node.trans[ch]

        curr_node.val = value

    def match_all (self, word):
        ret = []
        curr_node = self.root
    
        for ch in word:
            curr_node, val = self.__walk (curr_node, ch)
            if not curr_node: 
                break
    
            if val:
                ret.append (val)

        return ret

class Dict (Trie):
    def __init__(self, fname):
        super (Dict, self).__init__()
        self.load(fname)

    def load(self, fname):
        file = codecs.open(fname, 'r', 'utf-8')
        for line in file:
            # TODO: examine why algorithm isn't using the frequencies
            freq, word = line.strip().split()
            self.add(word, word)
        file.close()

class CharFreqs (defaultdict):
    def __init__ (self, fname):
        super (CharFreqs, self).__init__(lambda:1)
        self.load(fname)

    def load (self, fname):
        file = codecs.open(fname, 'r', 'utf-8')
        for line in file:
            freq, ch = line.strip().split()
            self[ch] = freq
        file.close()
        
class MMSeg:
    class Chunk:
        def __init__ (self, words, chrs):
            self.words  = words
            self.lens   = map(lambda x:len(x), words)
            self.length = sum(self.lens)
            self.mean   = float(self.length) / len(words)
            self.var    = sum(map(lambda x: (x-self.mean)**2, self.lens)) / len(self.words)
            self.degree = sum([log(float(chrs[x])) for x in words if len(x)==1])

        def __str__ (self):
            return ' '.join(self.words).encode('UTF-8') + \
                   "(%f %f %f %f)" % (self.length, self.mean, self.var, self.degree)

        def __lt__ (self, other):
            return (self.length,  self.mean,  -self.var,  self.degree) <  \
                   (other.length, other.mean, -other.var, other.degree)

    def __init__(self, dic, chrs):
        self.dic  = dic
        self.chrs = chrs

    def __get_chunks (self, s, depth=3):
        ret = []
        def __get_chunks_it (s, num, segs):
            if (num == 0 or not s) and segs:
                ret.append(MMSeg.Chunk(segs, self.chrs))
            else:
                m = self.dic.match_all(s)
                if not m:
                    __get_chunks_it (s[1:], num-1, segs+[s[0]])
                for w in m:
                    __get_chunks_it (s[len(w):], num-1, segs+[w])
     
        __get_chunks_it (s, depth, [])
        return ret

    def segment (self, s):
        while s:
            chunks = self.__get_chunks(s)
            best = max(chunks)
            yield best.words[0]
            s = s[len(best.words[0]):]

if __name__ == "__main__":
    dic = Dict("words.dic")
    chrs = CharFreqs("chars.dic")
    mmseg = MMSeg(dic, chrs)

    enc = sys.getfilesystemencoding()
    while True:
        try:
            s = input("Test String: ")
        except:
            break

        print("Test Result: ", end=' ')
        for w in mmseg.segment(s):
            print(w, end=' ')
        print('\n')

# -*- indent-tabs-mode: nil -*- vim:et:ts=4
