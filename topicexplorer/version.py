"""Version information with Lazy Loading"""
import types
import sys


class _VersionModule(types.ModuleType):

    @property
    def __version__(self):
        return "1.0b135"

    @property
    def __pretty_version__(self):
        from topicexplorer.update import get_dist
        from pip.utils import dist_is_editable
        dist = get_dist('topicexplorer')
        __pv__ = None
        if dist_is_editable(dist):
            import subprocess
            __pv__ = subprocess.check_output(
                'git describe --long --tags --always --dirty',
                cwd=dist.location, shell=True)
            __pv__ = __pv__.strip()
        return __pv__ or self.__version__

sys.modules[__name__] = _VersionModule("__version__")
