""" ixle.agents """

import os

from report import report

from ixle.python import sep, opj, splitext
from ixle.schema import Item

from .base import IxleAgent, IxleDBAgent,  KeyIterator, ItemIterator
from .janitor import Janitor, StaleChecker
from .sizer import Sizer
from .filer import Filer
from .stamper import Stamper
from .typer import Typer

#FIXME
def find_empties(db, field, items=False):
    """ finds keys where the field@field_name is empty """
    query = """
    function(doc){
    if(doc.""" + field + """){}
    else{emit(doc._id, null)}}
    """
    tmp_view = db.query(query)
    for r in tmp_view:
        if items:
            yield Item.load(db, r.key)
        else:
            yield r.key

class Md5er(ItemIterator):

    def callback(self, item, **kargs):
        if not item.md5:
            print item.fname
            result = self.run_and_collect('md5sum "' + item.abspath + '"')
            result = result.split()[0]
            item.md5 = result
            print '  ',result
            self.save(item)

class Indexer(IxleAgent):
    """ only gets new content, and
        refuses to touch anything already
        mentioned in db
    """
    requires_path = True
    provides = 'fname fext _id'.split()

    def __call__(self):
        self.index()

    def callback(self, id=None, **kargs):
        if self.is_ignored(id):
            return
        assert id is not None, 'this callback takes an id'
        abs_path = id
        rel_name = abs_path.split(sep)[-1]
        extension = splitext(rel_name)
        item = Item(fname=rel_name.decode('utf-8'),
                    fext=extension,
                    _id=abs_path.decode('utf-8'))
        print item.fname
        self.save(item)

    def index(self):
        report('running index for', self.path)
        for root, _dir, files in os.walk(self.path):
            for rel_name in files:
                self.callback(id=opj(root, rel_name))
