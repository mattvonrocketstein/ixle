""" ixle.agents.blacklist
"""

from report import report

from ixle.python import ope
from ixle.schema import Item
from .base import ItemIterator, IxleDBAgent
from .mixins import DestructionMixin

class BlacklistFext(IxleDBAgent, DestructionMixin):
    nickname = 'blacklist_fext'

    @property
    def query(self):
        item = Item.objects.get(path=self.path)
        return Item.objects.filter(fext=item.fext)

    def _get_callback_args(self, key, item):
        return dict(item=item, fname=None)

    def callback(self, item, fname=None, **kargs):
        self.delete_item(item)


class BlacklistFname(BlacklistFext):
    nickname = 'blacklist_fname'
    def callback(self, *args, **kargs):
        NIY
