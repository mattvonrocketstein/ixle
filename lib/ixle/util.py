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
from ixle._atexit import handle_exit

def wrap_kbi(fxn):
    def cleanup():
        print "exiting.."
    def newf(*args, **kargs):
        with handle_exit(cleanup):
            fxn(*args, **kargs)
    return newf

def conf():
    from ixle import settings
    return settings.Settings()

def report_if_verbose(*args, **kargs):
    # TODO:
    pass

def get_or_create(DB_NAME):
    from ixle.settings import Settings
    server = Settings().server
    if DB_NAME not in server:
        report("creating database {0} on {1} ".format(DB_NAME, server))
        server.create(DB_NAME)
    db = server[DB_NAME]
    return db

def database():
    """ get a handle for the main database object """
    return conf().database

def _harvest(modyool, arg_pattern):
    """ retrieve functions from module iff they have
        exactly 1 argument and that argument==arg_pattern
    """
    names = set(dir(modyool)) - set(dir(__builtins__))
    matches = []
    count=0
    for name in names:
        count+=1
        obj = getattr(modyool, name)
        if callable(obj) and inspect.isfunction(obj):
            func_sig = pep362.Signature(obj)
            parameter_dict = func_sig._parameters
            if len(parameter_dict)==1 and \
               arg_pattern in parameter_dict:
                matches.append(obj)
    return dict([m.__name__, m] for m in matches)

def get_api():
    from ixle import api
    d_action = _harvest(api, 'directory')
    p_action = _harvest(api, 'path')
    out={}
    [ out.update(x) for x in [d_action, p_action] ]
    return out

def get_heuristics():
    """ mines heuristic functions out of ixle.heuristics.
        that means: any simple function that takes one
        argument where that argument is named "item".

        returns a dictionary of { fxn_name : fxn }
    """
    from ixle import heuristics
    return _harvest(heuristics, 'item')

def yield_items_from_rows(fxn):
    """ """
    raise Exception,'deprecated'

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
