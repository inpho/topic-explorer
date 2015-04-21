#!/bin/sh -e
cd demo-data
python ap.py
cd ..
echo "Training ap corpus with command:"
echo "vsm init demo-data/ap ap.ini"
echo "vsm train ap.ini -k 10 20 30 40 50 --iter 20 --context-type document -p 2"
echo ""
echo "Run 'vsm train -h' for more details on training your own corpus"
echo ""
vsm init demo-data/ap ap.ini
vsm train ap.ini -k 10 20 30 40 50 --iter 20 --context-type document -p 2 

