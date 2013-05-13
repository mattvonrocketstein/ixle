""" ixle.util
"""

import re, os
import datetime
import inspect
from itertools import imap

import pep362
from couchdb.client import ViewResults

from report import report
from ixle.python import ope
from ixle.schema import Item

def database():
    from ixle import settings
    return settings.Settings().database

def get_api():#....
    pass

def get_heuristics():
    """ mines heuristic functions out of ixle.heuristics.
        that means: any simple function that takes one
        argument where that argument is named "item".

        returns a dictionary of { fxn_name : fxn }
    """
    from ixle import heuristics
    names = set(dir(heuristics))-set(dir(__builtins__))
    matches = []
    for name in names:
        obj = getattr(heuristics, name)
        if callable(obj) and inspect.isfunction(obj):
            func_sig = pep362.Signature(obj)
            parameter_dict = func_sig._parameters
            if len(parameter_dict)==1 and \
               'item' in parameter_dict:
                matches.append(obj)
    return dict([m.__name__, m] for m in matches)

def yield_items_from_rows(fxn):
    """ """
    def new_fxn(*args, **kargs):
        view = fxn(*args,**kargs)
        assert isinstance(view, ViewResults)
        return imap( lambda row: Item.wrap(row.doc),
                     iter(view))
    return new_fxn

def modification_date(filename):
    """ """
    if ope(filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)
    else:
        report('cant get mod_date: '+filename)

R_SPLIT_DELIM = re.compile('[\W_]+')
def smart_split(x):
    """ splits on most delims """
    return R_SPLIT_DELIM.split(x)

def no_alphabet(x):
    """ argh FIXME """
    no_delim = ''.join(smart_split(x))
    return len(no_delim) == re.compile('\d*').match(no_delim).end()
