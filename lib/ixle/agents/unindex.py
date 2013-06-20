""" ixle.agents.unindex
"""

from .base import ItemIterator
from .mixins import DestructionMixin
class Unindex(DestructionMixin, ItemIterator):

    count = 1

    def callback(self, item=None, **kargs):
        print item,kargs
        self.delete_item(item)
        if self.count==1:
            self.count+=1
            from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
