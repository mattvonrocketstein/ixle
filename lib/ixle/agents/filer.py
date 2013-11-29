""" ixle.agents.filer """

from report import report
from ixle.python import ope
from .base import ItemIterator

class Filer(ItemIterator):

    nickname = 'filer'
    covers_fields = ['file_magic']
    DEBUG = True

    def callback(self, item=None, **kargs):
        if any([self.force, not item.file_magic]):
            if ope(item.path):
                # -b is "brief" option, meaning to not prepend filename
                cmd = 'file -b "{0}"'.format(item.path)
                result = self.run_and_collect(cmd)
                result = [ x.strip() for x in result.split(',') ]
                result = [x for x in result if x]
                item.file_magic = result
                self.report_status('{0} gives: {1}'.format(
                    item.path, result))
                self.save(item)
