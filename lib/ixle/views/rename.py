""" ixle.views.rename
"""
import shutil

from report import report

from ixle.views.search import ItemListView
from ixle.schema import Item
from ixle.python import isdir, ope
from ixle.views.search import ItemListView
from .base import View


class RenameView(ItemListView):

    template = 'rename.html'
    url      = '/rename'
    methods  = 'get post'.upper().split()

    def get_ctx(self, *args, **kargs):
        result = super(RenameView,self).get_ctx(*args, **kargs)
        result.update(
            is_dir=isdir(self['_']),
            suggestion=self['suggestion'])
        return result

    def get_queryset(self):
        q = self['_']
        assert ope(q)
        if isdir(q):
            result = Item.startswith(q)
        else:
            result = Item.objects.filter(path=q)
        return result

    def main(self):
        if self['new_name']:
            old_name=self['old_name']
            new_name=self['new_name']
            #shutil.move(old_name, new_name)
            if new_name==old_name:
                print 'nothing to do'
            else:
                is_dir = isdir(old_name)
                qs = self.get_queryset()
                shutil.move(old_name, new_name)
                print 'fs-move\n  ',old_name,'  ',new_name
                for item in qs:
                    new_path = item.path.replace(old_name, new_name)
                    print 'move-db\n  ',item.path,'  ',new_path
                    item.path = new_path
                    item.save()
                if is_dir:
                    return self.redirect('/browser?_='+new_name)
                else:
                    return self.redirect(item.detail_url())
        return super(RenameView, self).main()
        #return self.render()

class RepackageView(ItemListView):
    template = 'repackage.html'
    url      = '/repackage'
    methods  = 'get post'.upper().split()
    def main(self):
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        return "3"
    def get_queryset(self):
        from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
