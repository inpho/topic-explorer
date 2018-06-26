#!/bin/bash
SRCDOCS=`pwd`/docs/_build/html
echo $SRCDOCS

cd `pwd`/docs
make html

cd $SRCDOCS
MSG="Adding gh-pages docs for `git log -1 --pretty=short --abbrev-commit`"

TMPREPO=/tmp/docs/topic-explorer/
rm -rf $TMPREPO
mkdir -p -m 0755 $TMPREPO
echo $MSG

git clone git@github.com:inpho/topic-explorer.git $TMPREPO
cd $TMPREPO
git checkout gh-pages  ###gh-pages has previously one off been set to be nothing but html
cp -r $SRCDOCS/* $TMPREPO
git add -A
git commit -m "$MSG" && git push origin gh-pages
