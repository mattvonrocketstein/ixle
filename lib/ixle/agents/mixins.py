""" ixle.agents.mixins
"""
import os
from report import report
from ixle.python import now, ope
from couchdb.http import ResourceConflict


class DestructionMixin(object):

    def delete_file(self, key=None, item=None):
        report('deleting file')
        if key and item:
            self.record['errors'] += 1
            self.record['error'] = 'cant pass key and item to delete_file.'
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
        if not ope(key):
            self.record['errors'] += 1
            self.record['error']='file does not exist.'
        os.remove(key) # TODO: use unipath
        self.record['files_deleted'] += 1
        self.delete_record(key)

    def delete_item(self, item):
        item.delete()
        self.record['records_deleted'] += 1

    def delete_record(self, key):
        from ixle.schema import Item
        items = Item.objects.filter(path=key)
        for item in items:
            return self.delete_item(item)

class SaveMixin(object):
    # TODO: abstract
    def save(self, item, quiet=False):
        """ """
        item.t_last_seen = now()
        item.save()
        self.record['count_saved'] += 1
        return True

class ReportMixin(object):

    def report(self, *args, **kargs):
        if self.conf.quiet: return
        report(*args, **kargs)

    def complain_missing(self, apath=None):
        self.report('file missing. gone? not mounted?')
        self.record['files_missing']+=1

    def report_error(self, *args, **kargs):
        raise
        self.record['error_count'] += 1
        report(*args, **kargs)
        self.record['last_error'] = [ args, kargs ]

    def report_status(self, status):
        report(status)
        self.record['last_status'] = status
