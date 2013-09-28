""" ixle.schema.dsetting
"""
from mongoengine import Document as mDocument

import json
from report import report
from mongoengine import StringField


class DSetting(mDocument):
    # _id:   absolute path to file (also the primary key)
    name   = StringField(required=True)
    value  = StringField(default='None')

    @classmethod
    def database(kls):
        from ixle.dsettings import get_or_create_settings_database
        return get_or_create_settings_database()

    def encode(self, v):
        self.value = json.dumps(v)
        self.save()
        report("saved {0} for setting @ {1}".format(v, self))

    def decode(self):
        if not self.value or self.value=="null":
            return None
        return self.value and json.loads(self.value)

    @classmethod
    def get_or_create(kls, name=None):
        if name is None:
            assert kls.setting_name, 'blahblah'
        try:
            return kls.load(kls.database(), name)
        except ResourceNotFound:
            himself = kls(
                _id = name,
                value=getattr(kls, 'default_value', None))
            himself.save()
            return himself
