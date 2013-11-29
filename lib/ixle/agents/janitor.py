""" ixle.agents """

from report import report

from ixle.python import ope, ops
from ixle.agents.base import KeyIterator, DestructionMixin
from ixle.agents.base import ItemIterator


class Janitor(ItemIterator, DestructionMixin):
    """ looks thru the database and finds various
        undesirables and removes them.  "undesirables"
        fall into a few categories currently:

        1) extension patterns that, according to the
           global-ignores in ixle.ini, should not be
           in the database at all.

        2) exact filenames in the dynamic blacklist setting

        NOTE: cannot be combined with stalechecker,
              because of shared folders, temporary
              mounts, etc

        TODO: use reduce here
    """

    nickname = 'janitor'
    def __call__(self, *args, **kargs):
        report("sweeping up anything matching: {0}".format(self.conf.ignore_globs))
        return super(Janitor, self).__call__(*args, **kargs)

    def is_blacklisted(self, key):
        from ixle.schema import DSetting
        blacklist = getattr(self, '_blacklist_cache', None)
        if blacklist is None:
            report('no cache found.. recomputing blacklist setting')
            # ?TODO: move this type of thing to DSetting.initialize()
            blacklist_setting, created = DSetting.objects.get_or_create(
                name='file_name_blacklist',
                defaults = dict(value='[]'))
            self._blacklist_cache = blacklist_setting.decode()
            return self.is_blacklisted(key)
        return ops(key)[-1] in blacklist

    def callback(self, item=None, fname=None, **kargs):
        if self.is_ignored(fname):
            #report("{0} should be ignored, deleting it.".format(fname))
            self.delete_record(fname)
        if self.is_blacklisted(fname):
            self.delete_file(key=fname)
            self.delete_record(key=fname)

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
        report('processed {0} records, total'.format(self.record['count_processed']))
        report('wiped {0} stale records'.format(self.record['records_deleted']))



    def callback(self,item=None, fname=None, **kargs):
        self.record['count_processed'] += 1
        if not ope(fname):
            print fname
            if self.force:
                self.delete_record(fname)
