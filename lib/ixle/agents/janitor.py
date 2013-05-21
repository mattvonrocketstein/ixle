""" ixle.agents """

from report import report

from ixle.python import ope
from ixle.agents.base import KeyIterator

class DestructionMixin(object):
    def get_count_deletion(self):
        return self.record['_deletion_count']

    def set_count_deletion(self,v):
        self.record['_deletion_count'] = self.get_count_deletion() + 1

    count_deletion = property(get_count_deletion, set_count_deletion)

    def delete_record(self, key):
        self.record['count_deletion'] += 1
        del self.database[key]


class Janitor(KeyIterator, DestructionMixin):
    """ looks thru the database and finds anything
        that, according to the global-ignores in
        ixle.ini, should not be in the database at
        all.

        NOTE: cannot be combined with stalechecker,
              because of shared folders, temporary
              mounts, etc

        TODO: use reduce here
    """

    nickname = 'janitor'
    def __call__(self, *args, **kargs):
        report("sweeping up anything matching: {0}".format(self.conf.ignore_globs))
        return super(Janitor,self).__call__(*args, **kargs)

    def callback(self, item=None, fname=None, **kargs):
        if self.is_ignored(fname):
            print fname
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
        report('processed {0} records, total'.format(self.record['count_processsed']))
        report('wiped {0} stale records'.format(self.record['count_deletion']))



    def callback(self,item=None, fname=None, **kargs):
        self.record['count_processsed'] += 1
        if not ope(fname):
            print fname
            if self.force:
                self.delete_record(fname)
