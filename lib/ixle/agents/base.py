""" ixle.agents.base
"""

import os
import fnmatch

from couchdb.http import ResourceConflict

from report import report
from ixle.schema import Item
from ixle.python import ope, abspath

class IxleAgent(object):

    def __init__(self, path=None, settings=None, force=False,**kargs):
        if self.requires_path:
           if not path or not ope(path):
               assert ope(path), 'path does not exist'
           path = abspath(path)
        self.path = path
        self.conf = settings
        self.force = force

    def run_and_collect(self, cmd):
        return os.popen(cmd).read().strip()

    def is_ignored(self, fname):
        ignored = self.conf.ignore_globs
        return any([ fnmatch.fnmatch(fname, x) \
                     for x in ignored ]) or \
               any([fnmatch.fnmatch(os.path.split(fname)[-1], x) \
                    for x in ignored ])

    def save(self, item):
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
            return """
            function(doc){
            if(doc['_id'].match('""" + self.path + """')){emit(doc['_id'], null)}
            }
            """
        else:
            return None

    def __iter__(self):
        """ dbagents dont require path, but when one is given then
            you only get back keys from underneath that path.
        """
        q = self.query
        if q is not None:
            result = [x.key for x in self.database.query(q) ]
        else:
            result = self.database
        return iter(result)

class KeyIterator(IxleDBAgent):
    def __call__(self):
        for key in self:
            self.callback(item=None, fname=key)

class ItemIterator(IxleDBAgent):

    def __call__(self):
        for key in self:
            self.callback(item=Item.load(self.database, key), fname=key)
