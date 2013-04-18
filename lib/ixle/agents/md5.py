"""
"""
from ixle.python import ope
from .base import ItemIterator

class Md5er(ItemIterator):
    nickname = 'md5'
    def callback(self, item, **kargs):
        if not item.md5:
            if not ope(item.abspath): return
            print item.fname
            result = self.run_and_collect(
                'md5sum "' + item.abspath.encode('utf-8') + '"')
            result = result.split()[0]
            item.md5 = result
            print '  ',result
            self.save(item)
