""" ixle.agents """

from report import report

from ixle.python import ope
from ixle.agents.base import KeyIterator

class DestructionMixin(object):
    def get_count_deletion(self):
        return getattr(self, '_deletion_count', 0)

    def set_count_deletion(self,v):
        self._deletion_count = self.get_count_deletion() + 1

    count_deletion = property(get_count_deletion, set_count_deletion)

    def delete_record(self, key):
        self.count_deletion += 1
        del self.database[key]


class Janitor(KeyIterator, DestructionMixin):
    """ looks thru the database and finds anything
        that, according to the global-ignores in
        ixle.ini, should not be in the database at
        all.

        NOTE: cannot be combined with stalechecker,
              because of shared folders, temporary
              mounts, etc
    """
    nickname = 'janitor'
    def callback(self, item=None, fname=None, **kargs):
        if self.is_ignored(fname):
            print fname
            #del self.database[fname]
            self.delete_record(fname)

class StaleChecker(KeyIterator, DestructionMixin):
    """ looks thru the database, checking for
        things that are stale. finding such
        things only flags them.. we wont
        remove them
    """
    nickname = 'stale'
    def __call__(self):
        super(StaleChecker,self).__call__()
        if not self.force:
            report(
                'finished with dry run.  if you really '
                'want to kill this stuff, pass --force')
        else:
            report('wiped {0} stale records'.format(
                self.count_deletion))


    def callback(self,item=None, fname=None, **kargs):
        if not ope(fname):
            print fname
            if self.force:
                self.delete_record(fname)
