rm ap.ini
topicexplorer -p benchmarks/init.`topicexplorer version`.prof init ap --rebuild --name "Associated Press 88-90 Sample" -q
topicexplorer -p benchmarks/prep.`topicexplorer version`.prof prep ap --lang en --high 2000 --low 5 -q
topicexplorer -p benchmarks/train.`topicexplorer version`.prof train ap -k 20 40 60 --context-type article --iter 20

