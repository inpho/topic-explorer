"""Version information with Lazy Loading"""
from builtins import str

import types
import sys


class _VersionModule(types.ModuleType):

    @property
    def __version__(self):
        return "1.0b233"

    @property
    def __pretty_version__(self):
        from topicexplorer.update import get_dist

        dist = get_dist('topicexplorer')
        __pv__ = None
        try:
            import subprocess
            __pv__ = subprocess.check_output(
                'git describe --long --tags --always --dirty',
                cwd=dist.location, shell=True)
            __pv__ = __pv__.decode('utf8')
            __pv__ = __pv__.strip()
            return __pv__
        except:
            return self.__version__

sys.modules[__name__] = _VersionModule("__version__")
