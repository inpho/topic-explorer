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

# Load the DLL manually to ensure its handler gets
# set before our handler.
basepath = imp.find_module('numpy')[1]
ctypes.CDLL(os.path.join(basepath, 'core', 'libmmd.dll'))
ctypes.CDLL(os.path.join(basepath, 'core', 'libifcoremd.dll'))

# Now set our handler for CTRL_C_EVENT. Other control event 
# types will chain to the next handler.
def handler(dwCtrlType, hook_sigint=thread.interrupt_main):
    if dwCtrlType == 0: # CTRL_C_EVENT
        hook_sigint()
        return 1 # chain to the next handler
    return 0 # chain to the next handler

win32api.SetConsoleCtrlHandler(handler, 1)    
