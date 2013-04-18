""" ixle.agents """

from ixle.schema import Item

from .base import IxleDBAgent,  KeyIterator
from ixle.python import ope

class Janitor(KeyIterator):
    """ looks thru the database and finds anything that, according
        to the global-ignores in ixle.ini, should not be in the
        database at all.

        NOTE: cannot be combined with stalechecker, because of shared
              folders, temporary mounts, etc

    """
    nickname='janitor'
    def callback(self, item=None, fname=None, **kargs):
        if self.is_ignored(fname):
            print fname
            del self.database[fname]

class StaleChecker(IxleDBAgent):
    """ looks thru the database, checking for
        things that are stale. finding such
        things only flags them.. we wont
        remove them
    """
    nickname = 'stale'
    def __call__(self):
        self.check()

    def callback(self, item=None, **kargs):
        print ' stale'

    def check(self):
        print 'only under', self.path
        for item_key in self.database:
            item = Item.load(self.database, item_key)
            print item.id
            if not ope(item.id):
                self.callback(item=item)
