""" ixle.schema.item
"""
import unipath

from mongoengine import Document as mDocument
from mongoengine import (StringField, BooleanField,
                         ListField, DateTimeField,
                         DictField, IntField)

from ixle.python import now, splitext

class Item(mDocument):
    """ Ixle Item: couchdb document abstraction for item on the filesystem """
    # _id:   absolute path to file (also the primary key)
    # fname: just the filename.  includes extensions
    # fext:  just the extension.  (for "foo.py", this is simply "py")
    path   = StringField(required=True)
    host   = StringField()
    tags   = DictField() #ListField(StringField())
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

    @classmethod
    def contains(self, s):
        return self.objects(__raw__={'path' : {'$regex':s}})

    @property
    def fname(self): return self.unipath.components()[-1]

    @property
    def unipath(self):
        assert self.path
        return unipath.FSPath(self.path)

    @property
    def dir(self): return self.unipath.parent


    # t_seen:      the date this was first seen by ixle
    # t_last_seen: the date this was last saved by ixle
    # t_mod:       the last-modified date the first time this was seen
    # t_last_mod:  the last-modified date the last time this was seen
    t_seen = DateTimeField()
    t_last_seen = DateTimeField()
    # http://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
    t_mod = DateTimeField()
    t_last_mod = DateTimeField()

    def exists(self):
        """ NOTE: False here does not mean the file is deleted or
                   moved! it could be that it's simply not mounted
        """
        return self.unipath.exists()

    @property
    def just_name(self):
        return self.fname[:-len(self.fname.ext)]

    @property
    def size_mb(self):
        """ get approx size in megabytes """
        return self.size and self.size*1.0/1024

    @property
    def dirname(self):
        return self.unipath.dirname
