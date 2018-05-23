#!/bin/bash
#CMD='coverage run -a --source topicexplorer --omit="topicexplorer/extensions/*.py,topicexplorer/lib/hathitrust.py"'
CMD="coverage run -a --source topicexplorer.init,topicexplorer.prep,topicexplorer.train,topicexplorer.server,topicexplorer.lib.pdf,topicexplorer.version,topicexplorer.demo,topicexplorer.update,topicexplorer.export,topicexplorer.tezimport"
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
sleep 15

test_url () {
    return $([[ $(curl -i $1 2>/dev/null | head -n 1 | cut -d$' ' -f2) == $2 ]])
}
test_url http://localhost:8000/ 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/ 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/50/ 400
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/topics 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/docs.json 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/docs.json?random=1 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/docs.json?q=bush 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/docs.json?id=AP900817-0118 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/topics.json 200
EXIT=$(($EXIT+$?))
test_url "http://localhost:8000/topics.json?q=bush|israel" 200
EXIT=$(($EXIT+$?))
test_url "http://localhost:8000/topics.json?q=foobar" 404
EXIT=$(($EXIT+$?))
test_url "http://localhost:8000/topics.json?q=a|the" 410
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/topics/1.json 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/topics/1.json?n=-20 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/topics.json?q=bush 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/cluster.csv 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/word_docs.json 400
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/word_docs.json?q=bush 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/docs_topics/AP900817-0118.json 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/doc_topics/AP900817-0118 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/20/docs/AP900817-0118 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/fulltext/AP900817-0118 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/icons.js 200
EXIT=$(($EXIT+$?))
test_url http://localhost:8000/description.md 200
EXIT=$(($EXIT+$?))

kill -2 $$
trap - INT

#$CMD -m topicexplorer.init www/papers --name "Papers" -q
#EXIT=$(($EXIT+$?))

$CMD -m topicexplorer.train ap.ini --rebuild -k 20 40 60 --iter 5 --context-type article --seed 37
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer.train ap.ini --continue --iter 15 --quiet
EXIT=$(($EXIT+$?))
# Testing triple continue function for singleprocessing, for issue #223
$CMD -m topicexplorer.train ap -k 20 --iter 20 --continue --quiet
EXIT=$(($EXIT+$?))

$CMD -m topicexplorer.train ap.ini --cluster 8
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer.train ap.ini --rebuild -k 20 40 60 --iter 10 --context-type article -p 2 --seed 92189
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer.export ap.ini -o ap.tez --include-corpus
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer.tezimport ap.tez -o ap2
EXIT=$(($EXIT+$?))
#$CMD -m topicexplorer update
#pip install -e .
$CMD -m topicexplorer version
EXIT=$(($EXIT+$?))
#pip install gitpython travispy
#$CMD -m topicexplorer update
# TODO: enable once status code for invalid branch is implemented
# EXIT=$EXIT+$?


# Testing the continue function for issues #222 and #223
$CMD -m topicexplorer.train ap -k 20 --iter 10 -p 2 --rebuild
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer.train ap -k 20 --iter 15 --continue --quiet
EXIT=$(($EXIT+$?))
$CMD -m topicexplorer.train ap -k 20 --iter 20 --continue --quiet
EXIT=$(($EXIT+$?))


$CMD -m unittest2
EXIT=$(($EXIT+$?))

pip install pytest
$CMD -m pytest tests/test_prep.py
EXIT=$(($EXIT+$?))

coverage report
echo "Exiting with code ${EXIT}"
exit $EXIT
