import numpy
import sys

import topicexplorer
import vsm

def main():
    print("OS:", sys.platform)
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)
    print("numpy version:", numpy.__version__)
    print("topicexplorer version:", topicexplorer.__version__)
    print("vsm version:", vsm.__version__)

if __name__ == '__main__':
    main()