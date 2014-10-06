#!/bin/sh
wget -q http://www.cs.princeton.edu/~blei/lda-c/ap.tgz
tar -xf ap.tgz
rm ap.tgz
python ap.py
