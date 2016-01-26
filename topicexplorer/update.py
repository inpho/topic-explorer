from pip.utils import (get_installed_version, dist_is_editable, dist_location)
from pip._vendor import pkg_resources
from pip._vendor.packaging.version import parse as parse_version

import subprocess
import json
import urllib2
from distutils.version import StrictVersion

def pypi_versions(package_name):
    # Based on: http://stackoverflow.com/a/27239645
    url = "https://pypi.python.org/pypi/%s/json" % (package_name,)
    data = json.load(urllib2.urlopen(urllib2.Request(url)))
    versions = data["releases"].keys()
    versions.sort(key=parse_version)
    return versions

def get_dist(dist_name):
    """Get the installed version of dist_name avoiding pkg_resources cache"""
    # Create a requirement that we'll look for inside of setuptools.
    req = pkg_resources.Requirement.parse(dist_name)

    # We want to avoid having this cached, so we need to construct a new
    # working set each time.
    working_set = pkg_resources.WorkingSet()

    # Get the installed distribution from our working set
    return working_set.find(req)


def update():
    dist = get_dist('topicexplorer')

    if dist_is_editable(dist):
        print "You have an editable install, so updates will be pulled from git."
        print "Your install directory is: {}\n".format(dist.location)
        for attempt in range(2):
            try:
                import git
                from git.exc import InvalidGitRepositoryError
                break
            except ImportError:
                install = raw_input(
                    "GitPython is required, but is not installed. Install? [Y/n] ")
                if install == '' or install.lower()[0] == 'y':
                    subprocess.check_call('pip install gitpython', shell=True)
                    # TODO: Add error handling for failed gitpython install
                    # Refresh local python path to reflect gitpython
                    import site
                    reload(site)

                    # attempt import once again
                    import git
                    reload(git)
                    from git.exc import InvalidGitRepositoryError
        else:
            print "GitPython is required to work with an editable install,"
            print "but it was not successfully installed.\n"
            return

        try:
            repo = git.Repo(dist.location)
        except InvalidGitRepositoryError:
            print "pip has detected an editable install, but the install directory"
            print "is not a valid git repository.\n"
            return

        if repo.is_dirty():
            print "There are uncommitted changes in your local repository."
            print "Please commit before running `vsm update`.\n"
            return

        if not repo.bare:
            #check for upstream updates
            branch = repo.active_branch
            commits_behind =list(repo.iter_commits(
                '{BRANCH}..origin/{BRANCH}'.format(BRANCH=branch.name)))
            commits_ahead =list(repo.iter_commits(
                'origin/{BRANCH}..{BRANCH}'.format(BRANCH=branch.name)))
            if commits_behind:
                print "Your branch is {} commits behind GitHub. Pulling changes.".format(len(commits_behind))
                repo.remotes.origin.pull()

                # reinstall, just in case dependencies or version have updated
                subprocess.check_call('python setup.py develop',
                    cwd=dist.location, shell=True)

                print "Your local branch was updated.\n"

            elif commits_ahead:
                print "Your branch is {} commits ahead of GitHub.".format(len(commits_ahead))
                push = raw_input("Do you want to push? [Y/n] ")
                if push == '' or push.lower()[0] == 'y':
                    repo.remotes.origin.push()
            else:
                print "Your local branch is synced with GitHub. No updates available.\n"

    else:
        # TODO: Check if pre-release, if so, then continue beta updates. 
        # If not, then wait for stable release. Allow for override flag.
        installed_version = parse_version(get_installed_version('topicexplorer'))
        pypi_version = parse_version(pypi_versions('topicexplorer')[-1])
        update_available = pypi_version > installed_version

        if update_available:
            subprocess.check_call(
                'pip install topicexplorer=={}'.format(pypi_version), 
                shell=True)

            print "Updated from {} to {}.\n".format(installed_version, pypi_version)
        else:
            print "You have the most recent release. No updates available.\n"

def main():
    update()
