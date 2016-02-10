"""Version information."""

@property
def __pretty_version__():
    from topicexplorer.update import get_dist
    from pip.utils import dist_is_editable
    dist = get_dist('topicexplorer')
    __pretty_version__ = None
    if dist_is_editable(dist):
        import subprocess
        __pretty_version__ = subprocess.check_output(
            'git describe --long --tags --always --dirty',
            cwd=dist.location, shell=True)
    return __pretty_version__

# The following line *must* be the last in the module, exactly as formatted:
# See http://stackoverflow.com/a/17626524
__version__ = "1.0b47"
