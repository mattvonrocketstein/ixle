""" ixle.agents.stamper
"""
from datetime import datetime

from humanize import naturaltime
from report import report

from ixle.util import modification_date, report_if_verbose
from .base import ItemIterator

class Stamper(ItemIterator):

    nickname = 'stamper'
    covers_fields = ['t_mod']

    def callback(self, item=None, **kargs):
        # t_seen:      the date this was first seen by ixle
        # t_mod:       the last-modified date the first time this was seen
        # t_last_mod:  the last-modified date the last time this was seen
        now = datetime.now()
        mod_date = modification_date(item.path)
        report_if_verbose(item.path)
        if any([self.force, mod_date]):
            item.t_last_mod = mod_date
        if any([self.force, not item.t_seen]):
            item.t_seen=now
        if any([self.force, not item.t_mod]):
            item.t_mod = mod_date
        report_if_verbose(
            dict(t_last_mod=naturaltime(item.t_last_mod),
                 t_seen=naturaltime(item.t_seen),
                 t_mod=naturaltime(item.t_mod)))

        # this is always adjusted by base-classes 'save'
        # t_last_seen: the date this was last seen by ixle
        self.save(item)
