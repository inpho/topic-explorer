import os
import sys
from time import sleep


import git
import pypandoc
from travispy import TravisPy
from travispy.errors import TravisError

from topicexplorer import __version__

### GIT CHECKS ###

# Initialize the repository
repo = git.Repo('.')

# Ensure that the branch is up to date
branch = repo.active_branch
commits_behind =list(repo.iter_commits(
    '{BRANCH}..origin/{BRANCH}'.format(BRANCH=branch.name)))
commits_ahead =list(repo.iter_commits(
    'origin/{BRANCH}..{BRANCH}'.format(BRANCH=branch.name)))

if not commits_ahead and not commits_behind:
    pass
elif commits_ahead and not commits_behind:
    print "Git branch '{}' ahead of origin. Pushing changes.".format(branch.name)
    repo.remotes.origin.push(branch.name)
else:
    print "Git branch '{}' out of sync. Aborting release.".format(branch.name)
    sys.exit(1)

current_commit = repo.head.commit.hexsha

### TODO: Automagically increment version number.

if __version__ not in repo.tags:
    print "Creating tag for release."
    repo.create_tag(__version__)

### TRAVIS-CI CHECKS ###
t = TravisPy.github_auth(open('.travis.key').read().strip())
print "Waitng for Travis-CI",
for attempt in range(900):
    try:
        branch = t.branch(__version__, 'inpho/topic-explorer')

        if current_commit != branch.commit.sha:
            raise RuntimeError("Need to wait for commit to sync.")
        if not branch.finished:
            raise RuntimeError("Need to wait for test to finish.")
        break
    except (TravisError, RuntimeError):
        print ".",
        sleep(10)
else:
    print "Travis build not complete. Aborting release."
    sys.exit(1)

if branch.finished and branch.passed:
    print "Travis build of release {} passed!".format(__version__) 
else:
    print "Travis build of release {} failed. Aborting release.".format(__version__)


### Convert documentation for PyPI ###
"""
pypandoc.convert('README.md', 'rst', outputfile='README.txt')
if sys.argv[-1] == 'test':
    os.system("python setup.py register -r pypitest")
else:
    os.system("python setup.py register")
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_egg upload")
os.remove('README.txt')
"""

print repo.remotes.origin.refs
if repo.remotes.origin.refs.get(__version__):
    print "Pushing tag for release to GitHub."
    repo.remotes.origin.push(__version__)
