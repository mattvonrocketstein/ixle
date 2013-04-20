""" ixle.agents.md5
"""
from report import report
from ixle.python import ope
from .base import ItemIterator

class Md5er(ItemIterator):
    nickname = 'md5'
    covers_fields = ['md5']

    def callback(self, item, fname=None, **kargs):
        report(item.fname)
        if not item.md5:
            if not ope(item.abspath):
                self.complain_missing(item.abspath)
                return
            result = self.run_and_collect(
                'md5sum "' + item.abspath + '"')
            try:
                result = result.split()[0]
            except:
                report('error collecting output from md5sum')
            else:
                item.md5 = result
                report(item.fname + '  ' + result)
                self.save(item)