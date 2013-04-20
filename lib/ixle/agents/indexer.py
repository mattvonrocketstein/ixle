""" ixle.agents.indexer
"""

import os

from report import report

from ixle.python import sep, opj, splitext
from ixle.schema import Item
from .base import IxleAgent


class Indexer(IxleAgent):
    """ only gets new content, and
        refuses to touch anything already
        mentioned in db
    """
    requires_path = True
    provides = 'fname fext _id'.split()
    nickname = 'index'

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
        report(item.fname)
        success = self.save(item)
        if not success and self.force:
            report('force-saving.. might be nasty')
            del self.database[item.id]
            self.save(item)

    def index(self):
        report('running index for', self.path)
        for root, _dir, files in os.walk(self.path):
            for rel_name in files:
                self.callback(id=opj(root, rel_name))