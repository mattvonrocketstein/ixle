""" ixle.python
"""
import os
opj = os.path.join
ope = os.path.exists
walk = os.path.walk
isdir = os.path.isdir
sep = os.path.sep
dirname = os.path.dirname
abspath = os.path.abspath
corkscrew_views = []

def splitext(fname):
    _, ext = os.path.splitext(fname)
    if ext and ext!='.':
        return ext[1:]
    return None
