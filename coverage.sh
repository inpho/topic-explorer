#!/bin/bash
#CMD='coverage run -a --source topicexplorer --omit="topicexplorer/extensions/*.py,topicexplorer/lib/hathitrust.py"'
CMD="coverage run -a --source topicexplorer.init,topicexplorer.prep,topicexplorer.train,topicexplorer.server"
rm -rf .coverage
coverage debug sys

EXIT=0
$CMD -m topicexplorer version
EXIT=$(($EXIT+$?))
echo "testing demo"
$CMD -m topicexplorer.demo --no-launch
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer.server -p 8000 --no-browser ap.ini &
DEMO_PID=$!
EXIT=$(($EXIT+$?))
sleep 15 
[ $(curl -i http://localhost:8000/docs.json 2>/dev/null | head -n 1 | cut -d$' ' -f2) == "200" ]
EXIT=$(($EXIT+$?))
[ $(curl -i http://localhost:8000/20/topics.json 2>/dev/null | head -n 1 | cut -d$' ' -f2) == "200" ]
EXIT=$(($EXIT+$?))

kill -INT $DEMO_PID

$CMD -m topicexplorer.train ap.ini --rebuild -k 20 40 60 --iter 20 --context-type article
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer update
# TODO: enable once status code for invalid branch is implemented
# EXIT=$EXIT+$?




coverage report
echo "Exiting with code ${EXIT}"
exit $EXIT
