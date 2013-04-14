""" ixle.agents.stamper
"""

from datetime import datetime
from .base import IxleDBAgent,  KeyIterator, ItemIterator
from ixle.util import modification_date

class Stamper(ItemIterator):
    def callback(self, item=None, **kargs):
        # t_seen:      the date this was first seen by ixle
        # t_last_seen: the date this was last seen by ixle
        # t_mod:       the last-modified date the first time this was seen
        # t_last_mod:  the last-modified date the last time this was seen
        now = datetime.now()
        mod_date = modification_date(item.id)
        print mod_date, item.id
        item.t_last_seen = now
        item._t_last_mod = mod_date
        if not item.t_seen:
            item.t_seen=now
        if not item.t_mod:
            item.t_mod = mod_date
