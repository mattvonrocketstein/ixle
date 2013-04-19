""" ixle.agents.dupes
"""

from .base import ItemIterator
from ixle.schema import DupeRecord
from ixle.agents.md5 import Md5er
from report import report

class Dupes(ItemIterator):
    """ saves size info """
    nickname = 'dupes'
    requires_path = False
    def __init__(self, *args, **kargs):
        super(Dupes,self).__init__(*args, **kargs)
        self.md5er = self.subagent(Md5er)

    @property
    def dupes_db(self):
        return self.conf.dupes_db

    def write_dupe(self, item1, item2):
        pass

    def find_matches(self, item, field):
        results = self.database._matching_values(
            field=field, value=getattr(item,field))
        return [x for x in results if x.id !=item.id]

    def seek_fname_collision(self,item):
        results = self.find_matches(item, 'fname')
        if not len(results): report(' - no dupes for this fname'); return
        item_ids = [row._id for row in results]
        reason = 'fname'
        self.record_collision(reason, item_ids)

    def seek_md5_collision(self, item):
        if not item.md5:
            report(' - md5 not set, calling subagent');
            self.md5er.callback(item)
        reason = 'md5'
        results = self.find_matches(item, 'md5')
        if not len(results): return
        item_ids = [row.value['_id'] for row in results] + [item._id]
        self.record_collision(reason, item_ids)

    def record_collision(self, reason, item_ids):
        item_ids = sorted(item_ids)
        event = DupeRecord(reason=reason, item_ids=item_ids)
        event.store(self.dupes_db)
        report(' - by {0}: found {1} dupes'.format(
            reason, len(item_ids)))

    def callback(self, item=None, **kargs):
        report(item._id)
        self.seek_fname_collision(item)
        self.seek_md5_collision(item)
