""" ixle.util
"""

import os
import datetime
from jinja2 import FileSystemLoader, Environment
from flask import render_template

from ixle.schema import Item
couch_js_dir = os.path.join(os.path.dirname(__file__),
                            'templates','couch_js')
assert os.path.exists(couch_js_dir)
LOADER = FileSystemLoader(couch_js_dir)

def modification_date(filename):
    """ """
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def rows2items(db, rows):
    """ """
    for row in rows:
       tmp=row.value.copy()
       tmp.pop('_rev')
       yield Item(**tmp)
       #yield Item.load(db, row.id)

def key_contains(db, substring):
    T = LOADER.load(Environment(),'key_search.js').render(substring=substring)
    return iter(db.query(T))
key_search = key_contains

def find_equal(db, fieldname, value):
    """ gives back an iterator over <Rows> where
        doc[fieldname] == value
    """
    T = LOADER.load(Environment(),
                    "find_equal.js").render(fieldname=fieldname,
                                            value=value)
    return iter(db.query(T))
