""" ixle.agents.base
"""
import os
import fnmatch
import random
from collections import defaultdict
from couchdb.http import ResourceConflict

from report import report

from ixle.schema import Item
#from ixle.query import javascript
from ixle.python import ope, abspath, now
from ixle.exceptions import FileDoesntExist
from .mixins import DestructionMixin, SaveMixin, ReportMixin

from ixle.util import wrap_kbi

class IxleAgent(SaveMixin, ReportMixin):

    is_subagent = False

    def __init__(self, path=None, settings=None,
                 items=[], fill=None,
                 force=False, **kargs):
        """ fill+path determine self.query """
        settings._engine.get_server() # HACK: ensure we're initialized
        self.record = defaultdict(lambda: 0)
        if self.requires_path:
           if not path or not ope(path):
               if not path or not ope(path):
                   raise FileDoesntExist(str(path))
        self.path = path and abspath(path)
        self.conf = settings
        self.force = force
        if fill:
            if path is not None:
                raise SystemExit('if you use --fill you cant '
                                 'use a path (and vice versa)')
        self.fill = fill
        if items:
            report('instantiated {0} with size {1} item-list'.format(
                self,len(items)))
            self.__iter__ = lambda himself: ([i.id, i] for i in items)
        self.record_invocation()

    def record_invocation(self):
        from ixle.schema import Event
        report("writing event for my birthday")
        e = Event(
            #reason="birthday::"+self.__class__.__name__
            reason = "birthday",
            details = dict(
                agent=self.__class__.__name__,
                path=self.path)
            )
        e.save()

    def get_progressbar(self, N, label='Files: '):
        assert N>0,str(N)
        from progressbar import (Percentage, ProgressBar,
                                 Bar,RotatingMarker, ETA, FileTransferSpeed)
        PBAR_WIDGETS = [label,
                        Percentage(), ' ',
                        Bar(marker=RotatingMarker()),
                        ' ', ETA(), ' ', ]
        return ProgressBar(widgets=PBAR_WIDGETS, maxval=N).start()

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
        try:
            return os.popen(cmd).read().strip()
        except IOError,e:
            report("IOError: " + str(e))
            return None

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

class QueryDecidingAspect(object):
    # TODO: use template
    def _query_from_path(self):
        return Item.startswith(self.path)

    def _query_from_fill(self):
        raise Exception,'niy'
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
        return q

class IxleDBAgent(QueryDecidingAspect, IxleAgent):
    """
            Not all DB Agents dont require path, but when one is given then
            you only get back keys from underneath that path.

            For ad-hoc queries, the query is determined with the following
            resolution-order:

              1. if subclass defines `_query_override`, use that
              2. if isinstance has self.path set, use that
                 (typically self.path is populated via commandline)
              3. if self.fill is True, a query will be generated which
                 can return everything that doesn't have that value set
              4. the default case is to assume we want all keys

    """
    requires_path = False

    def __iter__(self):
        t1 = now()
        report('starting query: ')
        q = self.query
        t2 = now()
        report('finished query ({0}s)'.format(t2-t1))
        return q
        """db = self.database
        if q is not None:
            raise Exception,'what do with query'+q
            #result = [ [x.key, Item.wrap(x.doc)]
            #          for x in db.query(q, include_docs=True) if x.key ]
        else:
            result = [ [ x, Item.load(db, x)] \
                       for x in db ]
        return iter(result)"""

    @wrap_kbi
    def __call__(self):
        kis = list(self)
        num_items = len(kis)
        if num_items:
            random_index = random.randint(0, num_items-1)
            report("WorkUnits: {0}".format(num_items))
            pbar = self.get_progressbar(
                num_items,
                label=self.__class__.__name__+':')
            report.console.draw_line()
            DEBUG = getattr(self, 'DEBUG', False)
            for index, (key, item) in enumerate([[x.path,x] for x in kis]):
                cb_kargs = self._get_callback_args(key, item)
                if False:
                    if index==1:
                        print ('\n\nfirst item, halting because DEBUG=True.'
                               '  enjoy a shell...')
                        from IPython import Shell;
                        Shell.IPShellEmbed(
                            argv=['-noconfirm_exit'])()
                    if index==random_index:
                        self.record['random_key'] = key
                #try:
                self.callback(**cb_kargs)
                #except Exception,e:
                #    err="ERROR IN CALLBACK:" + str(e)
                #    print err
                #    self.report_error(err)
                #    raise
                self.record['count_processsed'] += 1
                pbar.update(index)
            else:
                pass #report('list-iter was empty!')
            pbar.finish()
        report.console.draw_line()
        tmp = dict(self.record)
        print tmp
        return tmp

class KeyIterator(IxleDBAgent):
    """ agent base-class to iterate over keys in the 'ixle' database.
        keys are guaranteed absolute filepaths
    """
    def _get_callback_args(self, key, item):
        return dict(item=None, fname=key)

class ItemIterator(KeyIterator):
    """ agent base-class to iterate over items from the database """
    def _get_callback_args(self, key, item):
        result = super(ItemIterator, self)._get_callback_args(key, item)
        result.update(item=item)
        return result
