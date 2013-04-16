""" ixle.util
"""

import os
import datetime

from flask import render_template

from ixle.schema import Item

def modification_date(filename):
    """ """
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def rows2items(db, rows):
    """ """
    for row in rows:
        yield Item.load(db, row.id)

def key_contains(db, substring):
    T = render_template("key_search.js", substring=substring)
    return iter(db.query(T))
key_search = key_contains

def find_equal(db, fieldname, value):
    """ gives back an iterator over <Rows> where
        doc[fieldname] == value
    """
    T = render_template("find_equal.js", fieldname=fieldname, value=value)
    return iter(db.query(T))
