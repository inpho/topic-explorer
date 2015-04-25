import pypandoc
import os

pypandoc.convert('README.md', 'rst', outputfile='README.txt')
os.system("python setup.py register")
os.remove('README.txt')
