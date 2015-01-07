""" ixle.python
"""
import os
from datetime import datetime

now = datetime.now
opj = os.path.join
ops = os.path.split
ope = os.path.exists
walk = os.path.walk
isdir = os.path.isdir
sep = os.path.sep
mkdir = os.mkdir
expanduser = os.path.expanduser
dirname = os.path.dirname
abspath = os.path.abspath
corkscrew_views = []

def splitext(fname):
    _, ext = os.path.splitext(fname)
    if ext and ext!='.':
        return ext[1:]
    return None
