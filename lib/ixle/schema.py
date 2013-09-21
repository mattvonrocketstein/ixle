""" ixle.schema
"""
import os
import json

from datetime import datetime

import unipath as Unipath
from mongoengine import (StringField, BooleanField,
                         ListField, DateTimeField,
                         DictField, IntField)
from mongoengine import Document as mDocument


from report import report
from ixle.python import sep, ope, opj

class Event(mDocument):
    type = StringField()
    """ recorded event for an alleged duplicate """
    reason = StringField()
    item_ids = ListField(StringField(), default=[])
    resolution = StringField()
    stamp = DateTimeField(default=datetime.now)
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
                value=getattr(self,'default_value', None))
            himself.save()
            return himself

class Item(mDocument):
    """ Ixle Item: couchdb document abstraction for item on the filesystem """
    # _id:   absolute path to file (also the primary key)
    # fname: just the filename.  includes extensions
    # fext:  just the extension.  (for "foo.py", this is simply "py")
    path   = StringField(required=True)
    host   = StringField()
    tags   = ListField(StringField())
    fext   = StringField()

    # output for these fields is retrieved from posix command line utilities.
    # new processes are cheap.  the files these commands run on are potentially
    # huge, but the output is small so pipes should be inexpensive.  doing it
    # this way are probably better than anything in python's stdlib..

    md5        = StringField()            # via md5sum(1)
    size       = IntField()         # via du(1)
    file_magic = ListField(StringField(),
                           default=[])  # via file(1)
    mime_type  = StringField()            # via mimetypes module
    file_type  = StringField()
    is_movie   = BooleanField()

    @classmethod
    def startswith(self, name):
        #return self._get_collection().find(
        #    {'path' : {'$regex':'^'+name}})
        return self.objects(__raw__={'path' : {'$regex':'^'+name}})

    @property
    def fname(self): return self.unipath.components()[-1]

    @property
    def unipath(self):
        assert self.path
        return Unipath.FSPath(self.path)

    @property
    def dir(self): return self.unipath.parent


    # t_seen:      the date this was first seen by ixle
    # t_last_seen: the date this was last seen by ixle
    # t_mod:       the last-modified date the first time this was seen
    # t_last_mod:  the last-modified date the last time this was seen
    t_seen = DateTimeField()
    t_last_seen = DateTimeField()
    t_mod = DateTimeField()
    t_last_mod = DateTimeField()

    #def database(self):
    #    from ixle import settings
    #    return settings.Settings().database

    def exists(self):
        """ NOTE: False here does not mean the file is gone..
                  it could be that it's simply not mounted
        """
        return self.unipath.exists()

    @property
    def just_name(self):
        return os.path.splitext(self.fname)[0]

    @property
    def size_mb(self):
        """ get approx size in megabytes """
        return self.size and self.size*1.0/1024

    @property
    def dirname(self):
        return self.unipath.dirname
