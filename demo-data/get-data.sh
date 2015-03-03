#!/bin/sh
python ap.py
cd ..
python train.py demo-data/ap
python launch.py ap.ini
