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

class javascript:

    @staticmethod
    def get_template(name):
        return LOADER.load(Environment(), name)

    @staticmethod
    def key_startswith(substring):
        return javascript.get_template('key_startswith.js').render(
            substring=substring)

    @staticmethod
    def key_search(substring):
        return javascript.get_template('key_search.js').render(
            substring=substring)

def key_contains(db, substring):
    T = js.key_search(substring)
    return iter(db.query(T))
key_search = key_contains


def find_equal_js():
    return LOADER.load(Environment(),
                       "find_equal.js")

def find_equal(db, fieldname, value):
    """ gives back an iterator over <Rows> where
        doc[fieldname] == value
    """
    return iter(db.query(
        find_equal_js().render(fieldname=fieldname,
                               value=value)))
