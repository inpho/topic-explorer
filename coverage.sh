#!/bin/bash
#CMD='coverage run -a --source topicexplorer --omit="topicexplorer/extensions/*.py,topicexplorer/lib/hathitrust.py"'
CMD="coverage run -a --source topicexplorer.init,topicexplorer.prep,topicexplorer.train,topicexplorer.server"
rm -rf .coverage
coverage debug sys

$CMD -m topicexplorer version
$CMD -m topicexplorer.demo
$CMD -m topicexplorer.train ap.ini --rebuild -k 20 40 60 --iter 20 --context-type article
$CMD -m topicexplorer update

#TODO: Figure out test of launch
coverage report
