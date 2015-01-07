from mongoengine import Document as mDocument

from ixle.python import now

from mongoengine import (StringField,
                         ListField, DateTimeField,
                         DictField, )

class Event(mDocument):
    """ recorded event for an alleged duplicates, etc """
    type = StringField()
    reason = StringField()
    item_ids = ListField(StringField(), default=[])
    resolution = StringField()
    stamp = DateTimeField(default=now)
    details  = DictField()

    @property
    def jdetails(self):
        import json
        return json.dumps(self.details or {})

    @classmethod
    def database(self):
        from ixle.util import get_or_create
        db = get_or_create('ixle_events')
        return db
    db = database
