from subprocess import check_output, CalledProcessError
import sys


import git

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

### Build and upload to PyPI ###
try:
    if sys.argv[-1] == 'test':
        check_output("twine upload -r testpypi dist/*", shell=True)
    else:
        print("Building sdist and bdist_wheel")
        check_output("uv build", shell=True)

        print("Uploading wheel to PyPI.")
        check_output("twine upload dist/*", shell=True)

except CalledProcessError as e:
    print("\nFailed to upload the package to PyPI.\n")
    sys.exit(1)

print("Creating local tag for release.\n")
repo.create_tag(__version__)

print("Pushing tag to GitHub.\n")
repo.remotes.origin.push(__version__)

print("Release complete.\n")
