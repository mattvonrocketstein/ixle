""" ixle.agents.unindex
"""

from .base import ItemIterator
from .mixins import DestructionMixin
class Unindex(DestructionMixin, ItemIterator):

    count = 1

    def callback(self, item=None, **kargs):
        self.delete_item(item)
        if self.count==1:
            self.count+=1
