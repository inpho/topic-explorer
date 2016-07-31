"""
compatability module for IPython subprocesses to close cleanly and pass handlers
to the next handlers.

See: http://stackoverflow.com/a/15472811 for more details
"""
import os
import imp
import ctypes
import thread
import win32api
import sys

# Load the DLL manually to ensure its handler gets
# set before our handler.
basepath = imp.find_module('numpy')[1]
numpy_libmmd = os.path.join(basepath, 'core', 'libmmd.dll')
numpy_libifcoremd = os.path.join(basepath, 'core', 'libifcoremd.dll')
if os.path.exists(numpy_libmmd) and os.path.exists(numpy_libifcoremd):
    ctypes.CDLL(numpy_libmmd)
    ctypes.CDLL(numpy_libifcoremd)
else:
    import sys
    basepath = os.path.dirname(sys.executable)

    numpy_libmmd = os.path.join(basepath, 'Library/bin', 'libmmd.dll')
    numpy_libifcoremd = os.path.join(basepath, 'Library/bin', 'libifcoremd.dll')

    ctypes.CDLL(numpy_libmmd)
    ctypes.CDLL(numpy_libifcoremd)


# Now set our handler for CTRL_C_EVENT. Other control event
# types will chain to the next handler.
def handler(dwCtrlType, hook_sigint=thread.interrupt_main):
    if dwCtrlType == 0:  # CTRL_C_EVENT
        hook_sigint()
        return 1         # chain to the next handler
    return 0             # chain to the next handler

win32api.SetConsoleCtrlHandler(handler, 1)
