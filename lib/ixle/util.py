""" ixle.util
"""

import re, os
import datetime
from itertools import imap
from couchdb.client import ViewResults

from report import report
from ixle.python import ope
from ixle.schema import Item

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
