""" ixle.agents.base
"""
import os
import fnmatch

from couchdb.http import ResourceConflict

from report import report
from ixle.schema import Item
from ixle.python import ope, abspath

class IxleAgent(object):

    def complain_missing(self, apath=None):
        report('file missing. gone? not mounted?')

    def __init__(self, path=None, settings=None,
                 fill=None,
                 force=False, **kargs):
        if self.requires_path:
           if not path or not ope(path):
               assert ope(path), 'path does not exist: '+str(path)
        self.path = path and abspath(path)
        self.conf = settings
        self.force = force
        if fill:
            if path is not None:
                from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
                raise SystemExit('if you use --fill you cant '
                                 'use a path (and vice versa)')
        self.fill = fill

    def subagent(self,kls):
        return kls(path=self.path, settings=self.conf, force=self.force)

    def run_and_collect(self, cmd):
        """ for gathering the output from file(1) and md5(1) etc """
        return os.popen(cmd).read().strip()

    def is_ignored(self, fname):
        ignored = self.conf.ignore_globs
        return any([ fnmatch.fnmatch(fname, x) \
                     for x in ignored ]) or \
               any([fnmatch.fnmatch(os.path.split(fname)[-1], x) \
                    for x in ignored ])

    def save(self, item):
        """ """
        try:
            item.store(self.database)
        except ResourceConflict as err:
            failure_type, failure_msg = err.args[0]
            report(' {0}: {1}'.format(failure_type, failure_msg))

    @property
    def database(self):
        return self.conf.database

class IxleDBAgent(IxleAgent):
    requires_path = False

    @property
    def query(self):

        if self.path:
            q = """
            function(doc){
            if(doc['_id'].match('""" + self.path + """')){emit(doc['_id'], doc)}
            }
            """
        elif self.fill:
            from ixle.util import javascript
            q = javascript.find_empty(self.fill)
        else:
            q = None
        report("chose query: ")
    def __iter__(self):
        """ dbagents dont require path, but when one is given then
            you only get back keys from underneath that path.
        """
        q = self.query
        report('starting query')
        if q is not None:
            result = [x.key for x in self.database.query(q) ]
        else:
            result = self.database
        report('finished query')
        return iter(result)

class KeyIterator(IxleDBAgent):
    def __call__(self):
        for key in self:
            self.callback(item=None, fname=key)

class ItemIterator(IxleDBAgent):

    def __call__(self):
        keys = [key for key in self]
        report('working on {0} keys'.format(len(keys)))
        for key in keys:
            self.callback(item=Item.load(self.database, key), fname=key)
