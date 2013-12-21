""" ixle.schema.remote
"""

import os

import unipath

from mongoengine import Document as mDocument
from report import report

from ixle.python import opj, expanduser

from mongoengine import (StringField,
                         IntField)

from ixle.util import get_mounts_by_type

class Remote(mDocument):
    nickname = StringField(required=True)
    hostname = StringField(required=True)
    username = StringField(required=True)
    password = StringField(required=True)
    port     = IntField(default=22)
    protocol = StringField(default='sshfs')

    @classmethod
    def all_mounts(self):
        return get_mounts_by_type('fuse.sshfs')

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
                 ' -o cache_timeout=3600'
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
