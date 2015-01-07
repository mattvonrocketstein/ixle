""" ixle.schema.item
"""
import unipath
from report import report
from mongoengine import Document
from mongoengine import (StringField, BooleanField,
                         ListField, DateTimeField,
                         DictField, IntField)

from ixle.python import now, splitext, opj

class Item(Document):
    """ Ixle Item: couchdb document abstraction for item on the filesystem """
    # _id:   absolute path to file (also the primary key)
    # fname: just the filename.  includes extensions
    # fext:  just the extension.  (for "foo.py", this is simply "py")
    path   = StringField(required=True)
    host   = StringField()
    tags   = DictField()
    fext   = StringField()

    # output for these fields is retrieved from posix command line utilities.
    # new processes are cheap.  the files these commands run on are potentially
    # huge, but the output is small so pipes should be inexpensive.  doing it
    # this way are probably better than anything in python's stdlib..

    md5        = StringField()            # via md5sum(1)
    file_size  = IntField()               # via du(1)
    mime_type  = StringField()            # via mimetypes module
    file_type  = StringField()            #
    is_movie   = BooleanField()           #
    file_magic = ListField(               # via file(1)
        StringField(), default=[])

    def __str__(self):
        return '<Item: "{0}">'.format(self.fname)
    __repr__ = __str__

    @classmethod
    def startswith(self, name):
        name = name.replace('(', '\(').replace(')','\)')
        return self.objects(__raw__={ 'path' : {'$regex':'^'+name} })

    def siblings_from_db(self):
        return self.startswith(self.dir)

    @classmethod
    def contains(self, s):
        return self.objects(__raw__={'path' : {'$regex':s}})

    @property
    def fname(self):
        return self.unipath.components()[-1]

    @property
    def unipath(self):
        assert self.path
        return unipath.FSPath(self.path)

    @property
    def dir(self):
        """ """
        return self.unipath.parent

    def move(self, new_path):
        """ Item.move(new_path) effects a move
            both in the filesystem and on the
            database
        """
        import shutil
        from ixle.python import ope
        report("{0} \n     ->  {1}".format(self.path, new_path))
        assert unipath.FSPath(new_path).parent.exists(),'destination dir does not exist yet'
        assert ope(self.path), "item not found, is drive mounted?"
        shutil.move(self.path, new_path)
        self.path = new_path
        self.save()

    # t_seen:      the date this was first seen by ixle
    # t_last_seen: the date this was last saved by ixle
    # t_mod:       the last-modified date the first time this was seen
    # t_last_mod:  the last-modified date the last time this was seen
    t_seen = DateTimeField()
    t_last_seen = DateTimeField()
    # http://stackoverflow.com/questions/237079/how-to-get-file-creation-modification-date-times-in-python
    t_mod = DateTimeField()
    t_last_mod = DateTimeField()

    def detail_url(self):
        return '/detail?_=' + self.path

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
        return self.file_size and self.file_size*1.0/1024

    @property
    def dirname(self):
        return self.unipath.dirname

    def collapse(self):
        assert self.unipath.isdir()
        parent = self.unipath.parent
        for path in self.unipath.listdir():
            subitem = Item.objects.get(path=path)
            fname = subitem.fname
            new_path = opj(parent, fname)
            report("moving: ", path, new_path)
            subitem._move(new_path)

    def _move(self, new_path):
        import shutil
        shutil.move(self.path, new_path)
        self.path = new_path
        self.save()
