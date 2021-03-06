""" ixle.views.remotes
"""
import mongoengine
from ixle.views.base import View
from ixle.schema import Remote
from ixle.util import get_mounts_by_type

mtypes_of_interest = ['vboxsf', 'fuse.sshfs']

class UpdatingView(View):
    def _update(self, obj, data):
        for k,v in data.items(): setattr(obj,k,v)
        self._save(obj)

    def _save(self, obj):
        try:
            obj.save()
        except mongoengine.ValidationError,e:
            msg = str(e)
        else:
            msg = 'updated object successfully: {0}'.format(obj.nickname)
        self.flash(msg)

class RemotesView(UpdatingView):
    """ TODO: change name """
    url      = '/remotes'
    template = 'remotes.html'
    methods  = 'GET POST'.split()

    def handle_post(self):
        keys = [x for x in self.request.values if x!='data']
        nickname = keys[0].split('_')[0]
        data  = dict([[k.split('_')[1],
                       self[k]] for k in keys])
        if nickname=='NEWENTRY':
            if Remote.objects.filter(nickname=data['nickname']):
                self.flash(
                    ('this isnt new: entry already exists'
                     ' with nickname {0}').format(
                        data['nickname']))
                return
            else:
                obj = Remote()
        else:
            obj = Remote.objects.get(nickname=nickname)
        assert obj
        for k, v in data.items():
            if not v:
                data.pop(k)
            elif isinstance(self._fields[k], mongoengine.fields.IntField):
                data[k] = int(v)
        self._update(obj, data)

    @property
    def _fields(self):
        remote_fields = Remote._fields.copy()
        remote_fields.pop('id')
        for x in remote_fields:
            # ugh hack
            assert '_' not in x,'please, no underscores in fieldnames for Remote'
        return remote_fields

    def main(self):
        #detail = self['detail'] if self['detail'] else None
        #detail = Remote.objects.get(nickname=detail) if detail else None
        redirect = lambda:self.redirect(self.url)
        if self['mount']:
            detail = Remote.objects.get(nickname=self['mount'])
            if detail.is_mounted:
                self.flash("already mounted")
            else:
                mountpoint = detail.exec_mount()
                self.flash('mounted @ {0}'.format(mountpoint))
            return redirect()

        if self['delete_remote']:
            detail = Remote.objects.get(nickname=self['delete_remote'])
            detail.delete()
            return redirect()

        if self['umount']:
            detail = Remote.objects.get(nickname=self['umount'])
            success = detail.exec_umount()
            self.flash('unmount: {0}'.format(
                'success!' if success else 'failed.'))
            return redirect()
        elif self['data']: self.handle_post()
        remotes = Remote.objects.all()
        remote_fields = self._fields

        mounts = [ [mtype,get_mounts_by_type(mtype)] for mtype in \
                   mtypes_of_interest ]
        mounts = dict(mounts)
        return self.render(
            #detail=detail,
            remote_fields=remote_fields,
            all_mounts=Remote.all_mounts(),
            special_mounts = mounts,
            empty=object(),
            remotes=remotes)
