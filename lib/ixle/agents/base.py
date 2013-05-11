""" ixle.agents.base
"""
import os
import fnmatch

from couchdb.http import ResourceConflict

from report import report

from ixle.schema import Item
from ixle.query import javascript
from ixle.python import ope, abspath, now

def wrap_kbi(fxn):
    def newf(*args, **kargs):
        try:
            fxn(*args, **kargs)
        except KeyboardInterrupt:
            report("Exiting.")
    return newf

class SaveMixin(object):
    # TODO: abstract
    def save(self, item, quiet=False):
        """ """
        # TODO: count saves
        item.t_last_seen = now()
        try:
            item.store(self.database)
            return True
        except ResourceConflict as err:
            failure_type, failure_msg = err.args[0]
            if not quiet:
                report(' {0}: {1}'.format(failure_type, failure_msg))
            return False

class IxleAgent(SaveMixin):

    is_subagent = False

    def complain_missing(self, apath=None):
        report('file missing. gone? not mounted?')

    def __init__(self, path=None, settings=None, fill=None,
                 force=False, **kargs):
        """ fill+path determine self.query """
        if self.requires_path:
           if not path or not ope(path):
               assert ope(path), 'path does not exist: '+str(path)
        self.path = path and abspath(path)
        self.conf = settings
        self.force = force
        if fill:
            if path is not None:
                raise SystemExit('if you use --fill you cant '
                                 'use a path (and vice versa)')
        self.fill = fill

    # KISS with _ixle FORBIDDEN
    def subagent(self, kls):
        """ get another agent with the same settings
            as this agent.  useful when an agent like
            `Typer` requires as data some information
            that would normally be set by the `Mimer`
        """
        agent = kls(path=self.path,
                    settings=self.conf,
                    force=self.force)
        agent.is_subagent = True
        return agent

    def run_and_collect(self, cmd):
        """ for gathering the output from file(1) and md5(1) etc """
        cmd = cmd.replace('`','\`')
        return os.popen(cmd).read().strip()

    def is_ignored(self, fname):
        """ """
        ignored = self.conf.ignore_globs
        return any([ fnmatch.fnmatch(fname, x) \
                     for x in ignored ]) or \
               any([fnmatch.fnmatch(os.path.split(fname)[-1], x) \
                    for x in ignored ])

    @property
    def database(self):
        return self.conf.database

class IxleDBAgent(IxleAgent):
    requires_path = False

    # TODO: use template
    def _query_from_path(self):
        return ("function(doc){"
                "if(doc['_id'].match('""" + self.path + """'))"""
                "{emit(doc['_id'], doc)}}")

    def _query_from_fill(self):
        assert self.covers_fields
        assert len(self.covers_fields)==1
        return javascript.find_empty(self.covers_fields[0])

    def _query_override(self):
        return None

    @property
    def query(self):
        report.console.draw_line()
        if self._query_override() is not None:
            q = self._query_override()
        elif self.path:
            q = self._query_from_path()
        elif self.fill:
            q = self._query_from_fill()
        else:
            q = None
            report("chose query: (everything)")
        if q is not None:
            q = [x for x in q.split('\n') if x.strip()]
            q = '\n'.join(q)
            report("chose query: ")
            report(
                report.highlight.javascript(q),
                plain=True)

            report.console.draw_line()
        return q

    def __iter__(self):
        """ dbagents dont require path, but when one is given then
            you only get back keys from underneath that path.
        """
        q = self.query
        t1 = now()
        report('starting query')
        db = self.database
        if q is not None:
            result = [[x.key, Item.wrap(x.doc, db)] \
                      for x in db.query(q, include_docs=True) if x.key ]
        else:
            result = [ [ x, Item.load(db, x)] \
                       for x in db ]
        t2 = now()
        report('finished query ({0})'.format(t2-t1))
        return iter(result)

class KeyIterator(IxleDBAgent):
    @wrap_kbi
    def __call__(self):
        for key,item in self:
            self.callback(item=None, fname=key)

class ItemIterator(IxleDBAgent):
    @wrap_kbi
    def __call__(self):
        stuff=[x for x in self]
        report('working on {0} keys'.format(len(stuff)))
        for thing in stuff:
            key, item = thing
            self.callback(fname=key, item=item)
        report('finished.')
