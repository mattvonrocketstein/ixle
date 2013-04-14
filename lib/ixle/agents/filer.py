""" ixle.agents.filer """

from .base import ItemIterator

class Filer(ItemIterator):

    def callback(self, item=None, **kargs):
        if not item.file_magic:
            cmd = 'file "{0}"'.format(item.abspath)
            result = self.run_and_collect(cmd)
            result = result[result.find(':')+1:]
            result = [ x.strip() for x in result.split(',') ]
            result = [x for x in result if x]
            item.file_magic = result
            print item.abspath, result
            self.save(item)
