

def pypi_versions(package_name):
    # Based on: http://stackoverflow.com/a/27239645
    from pip._vendor.packaging.version import parse as parse_version
    import json
    import urllib2

    url = "https://pypi.python.org/pypi/%s/json" % (package_name,)
    data = json.load(urllib2.urlopen(urllib2.Request(url)))
    versions = data["releases"].keys()
    versions.sort(key=parse_version)
    return versions


def get_dist(dist_name):
    """Get the installed version of dist_name avoiding pkg_resources cache"""
    from pip._vendor import pkg_resources
    # Create a requirement that we'll look for inside of setuptools.
    req = pkg_resources.Requirement.parse(dist_name)

    # We want to avoid having this cached, so we need to construct a new
    # working set each time.
    working_set = pkg_resources.WorkingSet()

    # Get the installed distribution from our working set
    return working_set.find(req)


def process_exists(processname):
    # http://stackoverflow.com/a/29275361

    import subprocess
    import platform

    if platform.system() == 'Windows':
        tlcall = 'TASKLIST', '/FI', 'imagename eq %s' % processname
        # shell=True hides the shell window, stdout to PIPE enables
        # communicate() to get the tasklist command result
        tlproc = subprocess.Popen(tlcall, shell=True, stdout=subprocess.PIPE)
        # trimming it to the actual lines with information
        tlout = tlproc.communicate()[0].strip().split('\r\n')
        # if TASKLIST returns single line without processname: it's not running
        if len(tlout) > 1 and processname in tlout[-1]:
            return True
        else:
            return False
    else:
        raise NotImplementedError


def update(args=None):
    from pip.utils import (get_installed_version, dist_is_editable, dist_location)

    import platform
    import subprocess
    from subprocess import CalledProcessError

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
            print "Please commit before running `topicexplorer update`.\n"
            return

        if repo.active_branch != repo.heads.master:
            print "You are on the '{}' branch.".format(repo.active_branch),
            install = raw_input("Switch to the 'master' branch? [Y/n] ")
            if install == '' or install.lower()[0] == 'y':
                print "Switched to 'master' branch."
                repo.heads.master.checkout()
            else:
                print "You must switch to the 'master' branch to use `topicexplorer update`."
                return

        if not repo.bare:
            # check for upstream updates
            branch = repo.active_branch
            repo.remotes.origin.fetch(branch)
            commits_behind = list(repo.iter_commits(
                '{BRANCH}..origin/{BRANCH}'.format(BRANCH=branch.name)))
            commits_ahead = list(repo.iter_commits(
                'origin/{BRANCH}..{BRANCH}'.format(BRANCH=branch.name)))
            if commits_behind:
                print "Your branch is {} commits behind GitHub.".format(len(commits_behind))
                if platform.system() == 'Windows':
                    import sys
                    if sys.argv[0] != __file__:
                        print "Use the `python -m topicexplorer.update` command to update."
                        return
                    
                    # TODO: remove process_exists('vsm.exe') on 1.0rc1
                    if process_exists('topicexplorer.exe') or process_exists('vsm.exe'):
                        print "vsm is currently running,",
                        print "please close all Topic Explorers to update."
                        return

                print "Pulling changes."
                repo.remotes.origin.pull()
                # reinstall, just in case dependencies or version have updated
                try:
                    subprocess.check_call('python setup.py develop',
                                          cwd=dist.location, shell=True)
                except:
                    print "ERROR: Update did not comlete installation.\n"
                else:
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
        from pip._vendor.packaging.version import parse as parse_version

        installed_version = parse_version(get_installed_version('topicexplorer'))
        pypi_version = parse_version(pypi_versions('topicexplorer')[-1])
        update_available = pypi_version > installed_version

        if update_available:
            if platform.system() == 'Windows':
                import sys
                if sys.argv[0] != __file__:
                    print "Update available. Use the `python -m topicexplorer.update`",
                    print "command to update."
                    return
                # TODO: remove process_exists('vsm.exe') on 1.0rc1
                if process_exists('topicexplorer.exe') or process_exists('vsm.exe'):
                    print "topicexplorer is currently running, please close all Topic Explorers to update."
                    return

            try:
                subprocess.check_call(
                    'pip install topicexplorer=={} --no-cache-dir'.format(pypi_version),
                    shell=True)
            except CalledProcessError:
                print "ERROR: Update did not comlete installation.\n"
            else:
                print "Updated from {} to {}.\n".format(installed_version, pypi_version)
        else:
            print "You have the most recent release. No updates available.\n"


def main(args=None):
    update(args)

if __name__ == '__main__':
    main()
