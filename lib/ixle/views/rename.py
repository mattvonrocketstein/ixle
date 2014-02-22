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
                report('nothing to do')
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

from ixle.python import mkdir, ope, opj
class RepackageView(ItemListView):
    template = 'repackage.html'
    url      = '/repackage'
    methods  = 'post'.upper().split()

    def get_queryset(self):
        tmp = Item.objects.filter(path__in=self['siblings'].split(','))
        return tmp

    def get_ctx(self):
        ctx = super(RepackageView, self).get_ctx()
        ctx.update(
            root_dir = self['root_dir'],
            new_dir = self['new_dir'],
            siblings = self['siblings'].split(','))
        return ctx

    def main(self):
        sooper=super(RepackageView,self).main
        if not self['submit']:
            return sooper()
        else:
            qset = self.get_queryset()
            ctx = self.get_ctx()
            assert ope(ctx['root_dir']),"root dir doesnt exist!"
            new_dir = opj(ctx['root_dir'], ctx['new_dir'])
            if not ope(new_dir):
                report("creating: "+new_dir)
                mkdir(new_dir)
            else:
                report("target new_dir already exists",new_dir)
            for item in qset:
                if not ope(item.path):
                    report("sibling doesnt exist!", item.path)
                    continue
                else:
                    new_path = item.path.replace(ctx['root_dir'], new_dir)
                    report("{0} \n     ->  {1}".format(
                        item.path, new_path))
                    shutil.move(item.path, new_path)
                    item.path = new_path
                    item.save()
            return self.redirect('/browser?_='+new_dir)
