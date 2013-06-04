""" ixle.agents.sizer
"""
from report import report
from .base import ItemIterator

class Sizer(ItemIterator):
    """ saves size info """

    nickname = 'sizer'
    requires_path = False
    covers_fields = ['size']

    def get_size(self, item):
        # FIXME: use python
        if item.exists():
           tmp = self.run_and_collect(
               'du "' + item.abspath + '" 2>/dev/null').strip().split()
           if tmp:
               return int(tmp[0])
        else:
            self.record['count_errors'] += 1

    def callback(self, item=None, **kargs):
        if any([self.force, not item.size]):
            report(item.abspath)
            size = self.get_size(item)
            if size is not None:
                item.size = size
                self.report_status(str([size, item.fname]))
                self.save(item)
            else:
                self.complain_missing()
