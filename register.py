import pypandoc
import os
import sys

pypandoc.convert('README.md', 'rst', outputfile='README.txt')
if sys.argv[-1] == 'test':
    os.system("python setup.py register -r pypitest")
else:
    os.system("python setup.py register")
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_egg upload")
os.remove('README.txt')
