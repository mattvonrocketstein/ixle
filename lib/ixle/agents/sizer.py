""" ixle.agents.sizer
"""
from report import report
from .base import ItemIterator

class Sizer(ItemIterator):
    """ saves size info """

    nickname = 'sizer'
    requires_path = False
    covers_fields = ['file_size']

    def get_size(self, item):
        # FIXME: use python
        if item.exists():
           tmp = self.run_and_collect(
               'du "' + item.path + '" 2>/dev/null').strip().split()
           if tmp:
               return int(tmp[0])
        else:
            self.record['count_errors'] += 1

    def callback(self, item=None, **kargs):
        if any([self.force, not item.file_size]):
            self.report(item.path)
            size = self.get_size(item)
            if size is not None:
                item.file_size = size
                self.report_status(str([item.fname, size]))
                self.save(item)
            else:
                self.complain_missing()
