#!/usr/bin/env python
""" setup.py for ixle
"""
import os, sys
from setuptools import setup

# make sure that finding packages works, even
# when setup.py is invoked from outside this dir
this_dir = os.path.dirname(os.path.abspath(__file__))
if not os.getcwd()==this_dir:
    os.chdir(this_dir)

# make sure we can import the version number so that it doesn't have
# to be changed in two places. ixle/__init__.py is also free
# to import various requirements that haven't been installed yet
sys.path.append(os.path.join(this_dir, 'ixle'))
from version import __version__
sys.path.pop()

base_url = 'https://github.com/mattvonrocketstein/ixle/'
setup(
    name         = 'ixle',
    version      = __version__,
    description  = 'ixle indexes files',
    author       = 'mattvonrocketstein',
    author_email = '$author@gmail',
    url          = base_url,
    download_url = base_url+'/tarball/master',
    packages     = ['ixle'],
    keywords     = ['ixle','media'],
    entry_points = {
        'console_scripts': \
        ['pkg_script = ixle.bin.module:fxn', ] },
    install_requires=[],
    )
