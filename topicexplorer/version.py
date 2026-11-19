"""Version information with Lazy Loading"""

import types
import sys


class _VersionModule(types.ModuleType):

    @property
    def __version__(self):
        from importlib.metadata import version, PackageNotFoundError

        try:
            return version("topicexplorer")
        except PackageNotFoundError:
            # package is not installed (e.g. running from a source checkout)
            return "1.0b234"

    @property
    def __pretty_version__(self):
        from topicexplorer.update import install_location

        __pv__ = None
        try:
            import subprocess
            __pv__ = subprocess.check_output(
                'git describe --long --tags --always --dirty',
                cwd=install_location(), shell=True)
            __pv__ = __pv__.decode('utf8')
            __pv__ = __pv__.strip()
            return __pv__
        except:
            return self.__version__

sys.modules[__name__] = _VersionModule("__version__")
