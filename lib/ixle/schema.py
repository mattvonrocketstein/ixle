""" ixle.schema
"""
import os
import unipath as Unipath
from datetime import datetime
from ixle.python import ope, opj
from couchdb.mapping import Document
from couchdb.mapping import (TextField, IntegerField,
                             DateTimeField, ListField,
                             DictField, BooleanField)

from ixle.python import sep, ope

class Event(Document):
    type = TextField()
    """ recorded event for an alleged duplicate """
    reason = TextField()
    item_ids = ListField(TextField(), default=[])
    resolution = TextField()
    stamp = DateTimeField(default=datetime.now)
    details  = DictField()

class IxleDocument(object):
    def database(self):
        from ixle import util
        return util.database()

class DSetting(Document, IxleDocument):
    # _id:   absolute path to file (also the primary key)
    _id   = TextField()
    value  = TextField()

    @classmethod
    def get_or_create(self, name):
        return self.database()[name]

class Item(Document,IxleDocument):
    """ Ixle Item: couchdb document abstraction for item on the filesystem """
    # _id:   absolute path to file (also the primary key)
    # fname: just the filename.  includes extensions
    # fext:  just the extension.  (for "foo.py", this is simply "py")
    _id   = TextField()
    tags  = DictField()
    fname = TextField()
    fext  = TextField()

    # output for these fields is retrieved from posix command line utilities.
    # new processes are cheap.  the files these commands run on are potentially
    # huge, but the output is small so pipes should be inexpensive.  doing it
    # this way are probably better than anything in python's stdlib..

    md5        = TextField()            # via md5sum(1)
    size       = IntegerField()         # via du(1)
    file_magic = ListField(TextField(),
                           default=[])  # via file(1)
    mime_type  = TextField()            # via mimetypes module
    file_type  = TextField()
    is_movie   = BooleanField()
    has_body   = BooleanField()
    @property
    def body(self):
        doc = self.database().get(self.id, attachments=True) #inefficient
        attachments = doc.pop('_attachments', {})
        return attachments
        #self.database().get_attachment(self.id,'body.txt')

    @property
    def unipath(self):
        return Unipath.FSPath(self.id)

    @property
    def dir(self):
        return self.unipath.parent

    # t_seen:      the date this was first seen by ixle
    # t_last_seen: the date this was last seen by ixle
    # t_mod:       the last-modified date the first time this was seen
    # t_last_mod:  the last-modified date the last time this was seen
    t_seen = DateTimeField()
    t_last_seen = DateTimeField()
    t_mod = DateTimeField()
    t_last_mod = DateTimeField()

    def database(self):
        from ixle import settings
        return settings.Settings().database

    def raw_contents(self):
        return self.database().get_attachment(self, 'body.txt').read()

    def exists(self):
        """ NOTE: False here does not mean the file is gone..
                  it could be that it's simply not mounted
        """
        return ope(self.abspath)

    @property
    def just_name(self):
        return os.path.splitext(self.fname)[0]

    @property
    def abspath(self):
        try:
            return self.id.encode('utf-8')
        except UnicodeEncodeError,e:
            print self.id
            raise

    @property
    def size_mb(self):
        """ get approx size in megabytes """
        return self.size and self.size*1.0/1024

    @property
    def dirname(self):
        return self.abspath.split(sep)
