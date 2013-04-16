""" ixle.schema
"""
from datetime import datetime
from couchdb.mapping import Document
from couchdb.mapping import TextField, IntegerField, DateTimeField, ListField

class Item(Document):
    """ Ixle Item: couchdb document abstraction for item on the filesystem """
    # _id:   absolute path to file (also the primary key)
    # fname: just the filename.  includes extensions
    # fext:  just the extension.  (for "foo.py", this is simply "py")
    _id = TextField()
    fname = TextField()
    fext = TextField()

    # output for these fields is retrieved from posix command line utilities.
    # new processes are cheap.  the files these commands run on are potentially
    # huge, but the output is small so pipes should be inexpensive.  doing it
    # this way are probably better than anything in python's stdlib..

    md5 = TextField()         # via md5sum(1)
    size = IntegerField()     # via du(1)
    file_magic = ListField(TextField(), default=[])  # via file(1)
    mime_type = TextField()  # via mimetypes module
    file_type = TextField()

    # t_seen:      the date this was first seen by ixle
    # t_last_seen: the date this was last seen by ixle
    # t_mod:       the last-modified date the first time this was seen
    # t_last_mod:  the last-modified date the last time this was seen
    t_seen = DateTimeField(default=datetime.now)
    t_last_seen = DateTimeField(default=datetime.now)
    t_mod = DateTimeField(default=datetime.now)
    t_last_mod = DateTimeField(default=datetime.now)

    @property
    def abspath(self):
        return self.id
