#!/bin/sh -e
cd demo-data
python ap.py
cd ..
echo "Training ap corpus with command:"
echo "vsm train -k 10 20 30 40 50 60 70 80 90 100 --iter 20 -p 2 demo-data/ap"
echo ""
echo "Run 'vsm train -h' for more details on training your own corpus"
echo ""
vsm init demo-data/ap ap.ini
vsm train -k 10 20 --iter 20 -p 2 ap.ini 
#vsm train -k 10 20 30 40 50 60 70 80 90 100 --iter 20 -p 2 ap.ini 

