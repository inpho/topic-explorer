#!/bin/bash
CMD="coverage run --source=topicexplorer --omit=topicexplorer/lib,topicexplorer/extensions"
rm -rf .coverage
$CMD topicexplorer/__main__.py version
$CMD topicexplorer/__main__.py demo
$CMD topicexplorer/__main__.py train ap.ini 
$CMD topicexplorer/__main__.py launch
$CMD topicexplorer/__main__.py update
