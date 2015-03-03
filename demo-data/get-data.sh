#!/bin/sh -e
python ap.py
cd ..
python train.py -k 10 20 30 40 50 60 70 80 90 100 --iter 20 demo-data/ap
