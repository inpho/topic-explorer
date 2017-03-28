#!/bin/bash
#CMD='coverage run -a --source topicexplorer --omit="topicexplorer/extensions/*.py,topicexplorer/lib/hathitrust.py"'
CMD="coverage run -a --source topicexplorer.init,topicexplorer.prep,topicexplorer.train,topicexplorer.server"
rm -rf .coverage
coverage debug sys

EXIT=0
$CMD -m topicexplorer version
EXIT=$EXIT+$?
$CMD -m topicexplorer.demo
EXIT=$EXIT+$?
$CMD -m topicexplorer.train ap.ini --rebuild -k 20 40 60 --iter 20 --context-type article
EXIT=$EXIT+$?
$CMD -m topicexplorer update
# TODO: enable once status code for invalid branch is implemented
# EXIT=$EXIT+$?

coverage report
echo 'Exiting with code $EXIT'
exit $EXIT
