""" ixle.events
"""

import os

from .base import ItemIterator
from ixle.schema import Event
from ixle.agents.md5 import Md5er
from report import report

class Events(ItemIterator):
    """ saves size info """

    nickname = 'events'
    requires_path = False

    def __init__(self, *args, **kargs):
        super(Events, self).__init__(*args, **kargs)
        self.md5er = self.subagent(Md5er)
        self.collisions = dict(md5=[], fname=[])

    @property
    def events_db(self):
        return self.conf.events_db

    def write_dupe(self, item1, item2):
        pass

    def find_matches(self, item, field):
        results = self.database._matching_values(
            field=field, value=getattr(item,field))
        return [x for x in results if x.id !=item.id]

    def seek_fname_collision(self, item):
        if not len(os.path.splitext(item.fname)[0]) > 4:
            # does anyone really want to see how
            # many 1.mp3's you have? probably no.
            return
        results = self.find_matches(item, 'fname')
        if not len(results):
            #report(' - no events for this fname');
            return
        item_ids = [row.value['_id'] for row in results]
        if len(item_ids)>1:
            reason = 'fname'
            self.record_collision(reason, item_ids, item)

    def seek_md5_collision(self, item):
        if not item.md5:
            report(' - md5 not set, calling subagent');
            self.md5er.callback(item)
        reason = 'md5'
        results = self.find_matches(item, 'md5')
        if not len(results): return
        item_ids = [row.value['_id'] for row in results] + [item._id]
        self.record_collision(reason, item_ids, item)

    def record_collision(self, reason, item_ids, item=None):
        self.collisions[reason] += item_ids
        item_ids = sorted(item_ids)
        event = Event(reason=reason, item_ids=item_ids,
                      details=dict(md5=item.md5))
        event.store(self.events_db)
        report(' - by {0}: found {1} events'.format(
            reason, len(item_ids)))

    def callback(self, item=None, **kargs):
        report(item._id)
        if item._id not in self.collisions['fname']:
            self.seek_fname_collision(item)
        if item._id not in self.collisions['md5']:
            self.seek_md5_collision(item)
