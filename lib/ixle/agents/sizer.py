""" ixle.agents.sizer
"""

from .base import ItemIterator

class Sizer(ItemIterator):
    """ saves size info """

    nickname = 'sizer'
    requires_path = False

    def get_size(self, item):
        return int(self.run_and_collect('du "'+item.abspath+'"').split()[0])

    def callback(self, item=None, **kargs):
        if not item.size:
            size = self.get_size(item)
            item.size = size
            print size, item.fname
            self.save(item)
