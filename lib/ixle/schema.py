""" ixle.schema
"""
import os
import json
import unipath

import unipath as Unipath
from mongoengine import (StringField, BooleanField,
                         ListField, DateTimeField,
                         DictField, IntField)
from mongoengine import Document as mDocument


from report import report
from ixle.python import now, sep, ope, opj, expanduser

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

class Remote(mDocument):
    nickname = StringField(required=True)
    hostname = StringField(required=True)
    username = StringField(required=True)
    password = StringField(required=True)
    port     = IntField(default=22)
    protocol = StringField(default='sshfs')

    @classmethod
    def all_mounts(self):
        tmp = os.popen('mount -l -t fuse.sshfs').readlines()
        tmp = [x.strip() for x in tmp]
        return [x for x in tmp if x]

    @property
    def mount_dir(self):
        from ixle import settings
        try:
            mounts_dir = settings.Settings()['ixle']['mount_dir']
        except KeyError:
            raise Exception, 'settings[ixle][mount_dir] is not defined'
        mountpoint = opj(expanduser(mounts_dir), self.nickname)
        mountpoint = unipath.FSPath(mountpoint)
        if not mountpoint.exists():
            mountpoint.mkdir(parents=True)
            report("mountpoint did not exist.  created it: "+mountpoint)
        return mountpoint
    mountdir=mountpoint=mount_point=mount_dir

    def exec_umount(self):
        report("unmounting: {0}".format(self.mount_dir))
        error = os.system('fusermount -u {0}'.format(self.mount_dir))
        return not bool(error)

    def exec_mount(self):
        assert self.protocol=='sshfs',('sorry, only protocol "sshfs" '
                                       'is implemented, you are using: '+\
                                       str(self.protocol))
        target = self.mount_dir
        if self.is_mounted:
            return target

        cmd_t = ('echo "{passwd}"|'
                 'sshfs -p {port} -o password_stdin'
                 ' -o idmap=user {user}@{host}:/ {target}')
        cmd = cmd_t.format(
            passwd=self.password,
            port=self.port,
            user=self.username,
            host=self.hostname,
            target=target)

        report("executing mount: {0}".format(cmd))
        result = os.system(cmd)
        return target

    @classmethod
    def umount_all(self):
        report("unmounting everything..")
        for x in Remote.objects.all():
            if x.is_mounted:
                x.exec_umount()

    @property
    def is_mounted(self):
        myself='{0}@{1}:/'.format(self.username, self.hostname)
        for x in self.all_mounts():
            if myself in x:
                return True
        return False

import subprocess
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
