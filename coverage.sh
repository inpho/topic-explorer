#!/bin/bash
#CMD='coverage run -a --source topicexplorer --omit="topicexplorer/extensions/*.py,topicexplorer/lib/hathitrust.py"'
CMD="coverage run -a --source topicexplorer.init,topicexplorer.prep,topicexplorer.train,topicexplorer.server"
rm -rf .coverage ap
coverage debug sys

EXIT=0
$CMD -m topicexplorer version
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer.demo --no-launch
EXIT=$(($EXIT+$?))

# Special thanks on the `trap` semantics to:
# http://veithen.github.io/2014/11/16/sigterm-propagation.html
set -m # Reactivate monitor mode!
$CMD -m topicexplorer.server -p 8000 --no-browser ap.ini &
DEMO_PID=$!

trap 'echo "trying to kill $DEMO_PID" && kill -2 $DEMO_PID && echo "killed $DEMO_PID" && wait $DEMO_PID && echo "waited for $DEMO_PID";' INT
sleep 10

[ $(curl -i http://localhost:8000/docs.json 2>/dev/null | head -n 1 | cut -d$' ' -f2) == "200" ]
EXIT=$(($EXIT+$?))
[ $(curl -i http://localhost:8000/20/topics.json 2>/dev/null | head -n 1 | cut -d$' ' -f2) == "200" ]
EXIT=$(($EXIT+$?))
[ $(curl -i http://localhost:8000/ 2>/dev/null | head -n 1 | cut -d$' ' -f2) == "200" ]
EXIT=$(($EXIT+$?))
[ $(curl -i http://localhost:8000/20/ 2>/dev/null | head -n 1 | cut -d$' ' -f2) == "200" ]
EXIT=$(($EXIT+$?))
[ $(curl -i http://localhost:8000/topics 2>/dev/null | head -n 1 | cut -d$' ' -f2) == "200" ]
EXIT=$(($EXIT+$?))

kill -2 $$
trap - INT

$CMD -m topicexplorer.train ap.ini --rebuild -k 20 40 60 --iter 20 --context-type article
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer update
# TODO: enable once status code for invalid branch is implemented
# EXIT=$EXIT+$?

coverage report
echo "Exiting with code ${EXIT}"
exit $EXIT
