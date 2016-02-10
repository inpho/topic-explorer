from __version__ import __version__, __pretty_version__ as __pv__

@property
def __pretty_version__():
    if __pretty_version__ is None:
        __pretty_version__ = __version__
    return __pretty_version__

