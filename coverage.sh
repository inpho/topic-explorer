#!/bin/bash
CMD='coverage run -a --source topicexplorer --omit="topicexplorer/extensions/*.py,topicexplorer/lib/hathitrust.py"'

rm -rf .coverage
coverage debug sys

$CMD topicexplorer/__main__.py version
$CMD topicexplorer/__main__.py demo
$CMD topicexplorer/__main__.py train ap.ini --rebuild -k 20 40 60 --iter 20 --context-type article
$CMD topicexplorer/__main__.py update

#TODO: Figure out test of launch
coverage report
