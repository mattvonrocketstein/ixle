""" ixle.query
"""
from ixle.util import yield_items_from_rows
from ixle.python import dirname, ope, opj
from jinja2 import FileSystemLoader, Environment

couch_js_dir = opj(dirname(__file__), 'templates', 'couch_js')
assert ope(couch_js_dir)
LOADER = FileSystemLoader(couch_js_dir)

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

@yield_items_from_rows
def key_startswith(db, substring):
    return db.query(
        javascript.key_startswith(substring),
        include_docs=True)

@yield_items_from_rows
def equal_under(db, **kargs):
    """ gives back an iterator of <Items>
        for which doc[fieldname] == null
    """
    T = javascript.equal_under(**kargs)
    return db.query(T, include_docs=True)

@yield_items_from_rows
def key_contains(db, substring):
    """ gives back an iterator of <Items>
        for which doc[fieldname] == null
    """
    T = javascript.key_search(substring)
    return db.query(T, include_docs=True)
key_search = key_contains

@yield_items_from_rows
def find_empty(db, fieldname):
    """ gives back an iterator of <Items>
        for which doc[fieldname] == null
    """
    query = javascript.find_empty(fieldname)
    return db.query(query, include_docs=True)

# only strings
@yield_items_from_rows
def find_equal(db, fieldname, value):
    """ gives back an iterator over <Items>
        for which doc[fieldname] == value """
    query = javascript.find_equal(
        value=value, fieldname=fieldname)
    return db.query(query, include_docs=True)
