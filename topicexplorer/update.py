from importlib import reload

def pypi_versions(package_name):
    # Based on: http://stackoverflow.com/a/27239645
    from packaging.version import parse as parse_version
    import json
    import requests

    url = "https://pypi.python.org/pypi/%s/json" % (package_name,)
    data = requests.get(url, timeout=31).json()
    versions = data["releases"].keys()
    versions = sorted(versions, key=parse_version)
    return versions


def get_dist(dist_name):
    """Get the installed distribution metadata for dist_name."""
    from importlib.metadata import distribution, PackageNotFoundError

    try:
        return distribution(dist_name)
    except PackageNotFoundError:
        return None


def install_location():
    """Directory containing the topicexplorer package.

    For editable installs this is the source repository root; for regular
    installs it is the environment's site-packages directory.
    """
    import os.path
    import topicexplorer

    return os.path.dirname(os.path.dirname(os.path.abspath(topicexplorer.__file__)))


def dist_is_editable(dist_name='topicexplorer'):
    """Whether the package was installed in editable mode (PEP 610)."""
    from importlib.metadata import distribution, PackageNotFoundError

    try:
        raw = distribution(dist_name).read_text('direct_url.json')
    except (PackageNotFoundError, FileNotFoundError, KeyError):
        return False
    if not raw:
        return False
    import json

    return bool(json.loads(raw).get('dir_info', {}).get('editable'))


def process_exists(processname): # pragma: no cover
    # http://stackoverflow.com/a/29275361

    import subprocess
    import platform

    if platform.system() == 'Windows':
        tlcall = ['TASKLIST', '/FI', 'imagename eq %s' % processname]
        # shell=True hides the shell window, stdout to PIPE enables
        # communicate() to get the tasklist command result
        tlproc = subprocess.Popen(tlcall, shell=False, stdout=subprocess.PIPE)
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
    import platform
    import subprocess
    from subprocess import CalledProcessError

    dist = get_dist('topicexplorer')
    if dist is None:  # pragma: no cover
        print("Topic Explorer does not appear to be installed.\n")
        return

    location = install_location()

    if dist_is_editable():  # pragma: no cover
        print("You have an editable install, so updates will be pulled from git.")
        print("Your install directory is: {}\n".format(location))
        for attempt in range(2):
            try:
                import git
                from git.exc import InvalidGitRepositoryError
                break
            except ImportError:
                install = input(
                    "GitPython is required, but is not installed. Install? [Y/n] ")
                if install == '' or install.lower()[0] == 'y':
                    subprocess.check_call('uv pip install gitpython', shell=True)
                    # TODO: Add error handling for failed gitpython install
                    # Refresh local python path to reflect gitpython
                    import site
                    reload(site)

                    # attempt import once again
                    import git
                    reload(git)
                    from git.exc import InvalidGitRepositoryError
        else:
            print("GitPython is required to work with an editable install,")
            print("but it was not successfully installed.\n")
            return

        try:
            repo = git.Repo(location)
        except InvalidGitRepositoryError:
            print("pip has detected an editable install, but the install directory")
            print("is not a valid git repository.\n")
            return

        if repo.is_dirty():
            print("There are uncommitted changes in your local repository.")
            print("Please commit before running `topicexplorer update`.\n")
            return

        if repo.active_branch != repo.heads.master:
            print("You are on the '{}' branch.".format(repo.active_branch), end=' ')
            install = input("Switch to the 'master' branch? [Y/n] ")
            if install == '' or install.lower()[0] == 'y':
                print("Switched to 'master' branch.")
                repo.heads.master.checkout()
            else:
                print("You must switch to the 'master' branch to use `topicexplorer update`.")
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
                print("Your branch is {} commits behind GitHub.".format(len(commits_behind)))
                if platform.system() == 'Windows':  # pragma: no cover
                    import sys
                    if sys.argv[0] != __file__:
                        print("Use the `python -m topicexplorer.update` command to update.")
                        return
                    
                    # TODO: remove process_exists('vsm.exe') on 1.0rc1
                    if process_exists('topicexplorer.exe') or process_exists('vsm.exe'):
                        print("vsm is currently running,", end=' ')
                        print("please close all Topic Explorers to update.")
                        return

                print("Pulling changes.")
                repo.remotes.origin.pull()
                # reinstall, just in case dependencies or version have updated
                try:
                    subprocess.check_call('uv pip install -e .',
                                          cwd=location, shell=True)
                except:
                    print("ERROR: Update did not comlete installation.\n")
                else:
                    print("Your local branch was updated.\n")

            elif commits_ahead:
                print("Your branch is {} commits ahead of GitHub.".format(len(commits_ahead)))
                push = input("Do you want to push? [Y/n] ")
                if push == '' or push.lower()[0] == 'y':
                    repo.remotes.origin.push()
            else:
                print("Your local branch is synced with GitHub. No updates available.\n")

    else:
        # TODO: Check if pre-release, if so, then continue beta updates.
        # If not, then wait for stable release. Allow for override flag.
        from importlib.metadata import distribution
        from packaging.version import parse as parse_version

        installed_version = parse_version(distribution('topicexplorer').version)
        pypi_version = parse_version(pypi_versions('topicexplorer')[-1])
        update_available = pypi_version > installed_version

        if update_available:
            if platform.system() == 'Windows':  # pragma: no cover
                import sys
                if sys.argv[0] != __file__:
                    print("Update available. Use the `python -m topicexplorer.update`", end=' ')
                    print("command to update.")
                    return
                # TODO: remove process_exists('vsm.exe') on 1.0rc1
                if process_exists('topicexplorer.exe') or process_exists('vsm.exe'):
                    print("topicexplorer is currently running, please close all Topic Explorers to update.")
                    return

            try:
                cmd = ['uv', 'pip', 'install', f'topicexplorer=={pypi_version}', '--no-cache-dir']
                subprocess.check_call(cmd, shell=False)
            except CalledProcessError:
                print("ERROR: Update did not comlete installation.\n")
            else:
                print("Updated from {} to {}.\n".format(installed_version, pypi_version))
        else:
            print("You have the most recent release. No updates available.\n")


def main(args=None):
    update(args)

if __name__ == '__main__':
    main()
