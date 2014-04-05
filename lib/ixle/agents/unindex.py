""" ixle.agents.unindex
"""

from .base import ItemIterator
from .mixins import DestructionMixin

class Unindex(DestructionMixin, ItemIterator):
    nickname = 'unindex'
    def callback(self, item=None, **kargs):
        self.delete_item(item)
