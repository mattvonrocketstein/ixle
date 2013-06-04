""" ixle.agents.base
"""
import os
import fnmatch
import random
from collections import defaultdict
from couchdb.http import ResourceConflict

from report import report

from ixle.schema import Item
from ixle.query import javascript
from ixle.python import ope, abspath, now
from ixle.exceptions import FileDoesntExist

def wrap_kbi(fxn):
    def newf(*args, **kargs):
        out = None
        try:
            out = fxn(*args, **kargs)
        except KeyboardInterrupt:
            report("Exiting.")
        finally:
            return out
    return newf


class DestructionMixin(object):

    def delete_file(self, key=None, item=None):
        report('deleting file')
        if key and item:
            self.record['errors'] += 1
            self.record['error'] = 'cant pass key and item'
            return
        if not (key or item):
            self.record['errors'] += 1
            self.record['error'] = 'need either key or item'
            return
        if not key:
            if item is None:
                self.record['errors'] += 1
                self.record['error'] = 'item is none'
                return
            key = item and item.id
        if not key:
            self.record['errors'] += 1
            self.record['error'] = 'item is none'
        report('deleting file',key)
        if not os.path.exists(key):
            self.record['errors'] += 1
            self.record['error']='file does not exist.'
        os.remove(key) # TODO: use unipath
        self.record['files_deleted'] += 1
        self.delete_record(key)

    def delete_record(self, key):
        del self.database[key]
        self.record['records_deleted'] += 1


class SaveMixin(object):
    # TODO: abstract
    def save(self, item, quiet=False):
        """ """
        item.t_last_seen = now()
        try:
            item.store(self.database)
            self.record['count_saved']+=1
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

    def __init__(self, path=None, settings=None,
                 items=[], fill=None,
                 force=False, **kargs):
        """ fill+path determine self.query """
        self.record = defaultdict(lambda: 0)
        if self.requires_path:
           if not path or not ope(path):
               if not ope(path):
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

    def get_progressbar(self, N, label='Files: '):
        assert N>0,str(N)
        from progressbar import Percentage,ProgressBar,Bar,RotatingMarker,ETA,FileTransferSpeed
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
        report('starting query: ',q)
        db = self.database
        if q is not None:
            result = [[x.key, Item.wrap(x.doc)]
                      for x in db.query(q, include_docs=True) if x.key ]
        else:
            result = [ [ x, Item.load(db, x)] \
                       for x in db ]
        t2 = now()
        report('finished query ({0}s)'.format(t2-t1))
        return iter(result)

    @wrap_kbi
    def __call__(self):
        kis = list(iter(self))
        num_items = len(kis)
        if num_items:
            random_index = random.randint(0, num_items-1)
            report("WorkUnits: {0}".format(num_items))
            pbar = self.get_progressbar(
                num_items, label=self.__class__.__name__+':')
            report.console.draw_line()
            DEBUG = getattr(self, 'DEBUG', False)
            for index,(key, item) in enumerate(kis):
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
                try:
                    self.callback(**cb_kargs)
                except Exception,e:
                    self.report_error("ERROR IN CALLBACK:" + str(e))
                    raise
                self.record['count_processsed'] += 1
                pbar.update(index)
            else:
                pass #report('list-iter was empty!')
            pbar.finish()
        report.console.draw_line()
        tmp = dict(self.record)
        print tmp
        return tmp

    def report_error(self, *args, **kargs):
        self.record['error_count'] += 1
        report(*args, **kargs)
        self.record['last_error'] = [ args, kargs ]

class KeyIterator(IxleDBAgent):
    def _get_callback_args(self, key, item):
        return dict(item=None, fname=key)

class ItemIterator(KeyIterator):

    def _get_callback_args(self, key, item):
        result = super(ItemIterator, self)._get_callback_args(key, item)
        result.update(item=item)
        return result
