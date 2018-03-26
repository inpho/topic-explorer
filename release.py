from __future__ import print_function
from builtins import range
import os
from subprocess import check_output, CalledProcessError
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
    print("Git branch '{}' ahead of origin. Pushing changes.\n".format(branch.name))
    repo.remotes.origin.push(branch.name)
else:
    print("Git branch '{}' out of sync. Aborting release.\n".format(branch.name))
    sys.exit(1)

current_commit = repo.head.commit.hexsha

### Check version numbers are not already online
if __version__ in repo.tags and current_commit != repo.tags[__version__]:
    print("Local version tag already exists: ", __version__)
    print("Increment the version number and run release again.\n")
    sys.exit(1)
elif (__version__ in repo.remotes.origin.repo.tags and 
      current_commit != repo.remotes.origin.repo.tags[__version__]):
    print("GitHub version tag already exists: ", __version__)
    print("Increment the version number and run release again.\n")
    sys.exit(1)

# check for a no-travis flag
if sys.argv[-1] != '--no-travis':
    ### TRAVIS-CI CHECKS ###
    try:
        t = TravisPy.github_auth(open('.travis.key').read().strip())
    except IOError as e:
        if e.errno == 2:
            print(".travis.key file required to hold GitHub Auth Token.")
            url = "https://github.com/settings/tokens/new"
            url += "?scopes=repo_deployment,repo:status,write:repo_hook,read:org,user:email"
            url += "&description=travis%20ci%20token"
            # TODO: Prompt to open browser or automate token grab
            print(url + '\n')
            sys.exit(1)
        else:
            raise e
    except TravisError:
        if not open('.travis.key').read().strip():
            print(".travis.key file is empty. Fill with a GitHub Auth Token from:")
            url = "https://github.com/settings/tokens/new"
            url += "?scopes=repo_deployment,repo:status,write:repo_hook,read:org,user:email"
            url += "&description=travis%20ci%20token"
            # TODO: Prompt to open browser or automate token grab
            print(url)
        else:
            print(".travis.key file detected, but there was an error communicating with Travis.")
            print("Check your GitHub Auth Token or check the Travis status page at:")
            print("https://www.traviscistatus.com/")
        print(" ")
        sys.exit(1)
            
    print("Waitng for Travis-CI .", end=' ')
    for attempt in range(900):
        try:
            branch = t.branch(repo.active_branch, 'inpho/topic-explorer')
    
            if current_commit != branch.commit.sha:
                raise RuntimeError("Need to wait for commit to sync.")
            if not branch.finished:
                raise RuntimeError("Need to wait for test to finish.")
            break
        except (TravisError, RuntimeError):
            if sys.version_info.major == 3:
                print(".", end=' ', flush=True)
            else:
                print(".", end=' ')
                sys.stdout.flush()
            sleep(10)
    else:
        print("Travis build not complete. Aborting release.\n")
        sys.exit(1)

    if branch.finished and branch.passed:
        print("Travis build of release {} passed!\n".format(__version__)) 
    else:
        print("Travis build of release {} failed. Aborting release.\n".format(__version__))
        sys.exit(1)

### Convert documentation for PyPI ###
pypandoc.convert('README.md', 'rst', outputfile='README.txt')
try:
    if sys.argv[-1] == 'test':
        check_output("python setup.py register -r pypitest", shell=True)
    else:
        print("Registering package with PyPI.")
        check_output("python setup.py register", shell=True)

        print("Uploading source to PyPI.")
        check_output("python setup.py sdist upload", shell=True)

        print("Uploading wheel to PyPI.")
        check_output("python setup.py bdist_wheel upload", shell=True)

except CalledProcessError as e:
    print("\nFailed to register and upload the package to PyPI.\n")
    sys.exit(1)
finally:
    os.remove('README.txt')

print("Creating local tag for release.\n")
repo.create_tag(__version__)

print("Pushing tag to GitHub.\n")
repo.remotes.origin.push(__version__)

print("Release complete.\n")
