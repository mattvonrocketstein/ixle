""" ixle.agents.md5
"""
from report import report
from ixle.python import ope
from .base import ItemIterator

class Md5er(ItemIterator):
    nickname = 'md5'
    covers_fields = ['md5']
    DEBUG = True

    def callback(self, item, fname=None, **kargs):
        self.report(item.fname)
        if any([self.force, not item.md5]):
            if not item.exists():
                self.complain_missing(item.path)
                return
            try:
                result = self.run_and_collect(
                    'md5sum "' + item.path + '"')
                result = result.split()[0]
            except:
                self.report_error('error collecting output from md5sum')
            else:
                item.md5 = result
                #report(item.fname + '  ' + result)
                self.save(item)
