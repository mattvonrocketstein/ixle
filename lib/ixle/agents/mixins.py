""" ixle.agents.mixins
"""
import os
from report import report
from ixle.python import now
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
        if not os.path.exists(key):
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
        item = Item.objects.get(path=key)
        return self.delete_item(item)



class SaveMixin(object):
    # TODO: abstract
    def save(self, item, quiet=False):
        """ """
        if not item.item.t_last_seen = now()
        item.save() #store(self.database)
        self.record['count_saved'] += 1
        return True

class ReportMixin(object):

    def complain_missing(self, apath=None):
        report('file missing. gone? not mounted?')

    def report_error(self, *args, **kargs):
        self.record['error_count'] += 1
        report(*args, **kargs)
        self.record['last_error'] = [ args, kargs ]

    def report_status(self, status):
        report(status)
        self.record['last_status'] = status
