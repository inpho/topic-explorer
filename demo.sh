#!/bin/sh -e
cd demo-data
python ap.py
cd ..
echo "Training ap corpus with command:"
echo "python train.py -k 10 20 30 40 50 60 70 8090 100 --iter 20 -p 2 demo-data/ap"
echo ""
echo "Run 'python train.py -h' for more details on training your own corpus"
echo ""
python train.py -k 10 20 30 40 50 60 70 80 90 100 --iter 20 -p 2 demo-data/ap
