""" ixle.util
"""

import os
import datetime
from jinja2 import FileSystemLoader, Environment
from flask import render_template

from ixle.python import ope
from ixle.schema import Item

couch_js_dir = os.path.join(os.path.dirname(__file__),
                            'templates','couch_js')
assert os.path.exists(couch_js_dir)
LOADER = FileSystemLoader(couch_js_dir)

def modification_date(filename):
    """ """
    if ope(filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

def rows2items(db, rows, approx=False):
    """ """
    for row in rows:
       if not approx:
           tmp=row.value.copy()
           tmp.pop('_rev')
           yield Item(**tmp)
       else:
           yield Item.load(db, row.id)

class javascript:

    @staticmethod
    def get_template(name):
        return LOADER.load(Environment(), name)

    @staticmethod
    def equal_under(substring=None, fieldname=None, value=None):
        if value==None: value='null'
        else:
            if not value.startswith("'"):
                value="'{0}'".format(value)
        return javascript.get_template('equal_under.js').render(
            substring=substring, fieldname=fieldname, value=value)

    @staticmethod
    def key_startswith(substring):
        return javascript.get_template('key_startswith.js').render(
            substring=substring)

    @staticmethod
    def find_equal(fieldname=None, value=None):
        assert fieldname and value
        return javascript.get_template('find_equal.js').render(
            fieldname=fieldname, value=value)

    @staticmethod
    def key_search(substring):
        return javascript.get_template('key_search.js').render(
            substring=substring)

    @staticmethod
    def find_empty(fieldname):
        return javascript.get_template('find_empty.js').render(
            fieldname=fieldname)

def equal_under(db, **kargs):
    T = javascript.equal_under(**kargs)
    return iter(db.query(T))

def key_contains(db, substring):
    T = javascript.key_search(substring)
    return iter(db.query(T))
key_search = key_contains

def find_empty(db, fieldname):
    query = javascript.find_empty(fieldname)
    return iter(db.query(query))

# only strings
def find_equal(db, fieldname, value):
    """ gives back an iterator over <Rows> where
        doc[fieldname] == value """
    query = javascript.find_equal(
        value=value, fieldname=fieldname)
    return iter(db.query(query))
