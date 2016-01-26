from pip.utils import (get_installed_version, dist_is_editable, dist_location)
from pip._vendor import pkg_resources
from pip._vendor.packaging.version import parse as parse_version

from subprocess import Popen
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
    te_dist = get_dist('topicexplorer')
    vsm_dist = get_dist('vsm')

    if dist_is_editable(te_dist):
        # call git within directory

        for i in attempt(2):
            try:
                import git
                from git.exc import InvalidGitRepositoryError
            except ImportError:
                install = raw_input("GitPython is required, but is not installed. Install? ")
                if install.lower()[0] == 'y':
                    Popen('pip install gitpython')
                    # TODO: Add error handling for failed gitpython install
                    # TODO: Refresh local python path to reflect gitpython
        else:
            print "GitPython is required to work with an editable install,"
            print "but it was not successfully installed."
            print "Exiting."
            return

        try:
            repo = git.Repo(te_dist.location)
        except InvalidGitRepositoryError:
            print "pip has detected an editable install, but the install directory"
            print "is not a valid git repository."
            print "Your install directory is: {}".format(te_dist.location)
            return

        if repo.is_dirty():
            print "There are uncommitted changes in your local repository."
            print "Please commit before running `vsm update`."
            print "Your local repository is: {}".format(te_dist.location)
            return

        if not repo.bare:
            #check for upstream updates
            list(repo.iter_commits('BRANCH..BRANCH@{u}'))
            repo.pull()

            # reinstall, just in case dependencies have updated
            Popen('python setup.py develop', cwd=te_dist.location)

    else:
        installed_version = parse_version(get_installed_version('topicexplorer'))
        pypi_version = parse_version(pypi_versions('topicexplorer')[-1])
        update_available = pypi_version > installed_version

        if update_available:
            Popen('pip install topicexplorer=={}'.format(pypi_version))

