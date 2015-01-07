""" ixle.views.rename
"""
import shutil

from report import report

from ixle.python import ope
from ixle.views.search import ItemListView
from ixle.schema import Item
from ixle.python import isdir

class CollapseDirView(ItemListView):
    template = 'collapse_dir.html'
    url      = '/collapse_dir'
    methods  = 'get post'.upper().split()

    def get_ctx(self, *args, **kargs):
        result = super(CollapseDirView, self).get_ctx(*args, **kargs)
        result.update(
            is_dir=isdir(self['_']))
        return result

    def get_queryset(self):
        q = self['_']
        assert ope(q)
        assert isdir(q)
        result = Item.startswith(q)
        return result

    def main(self):
        if self['do_it']:
            assert ope(self['_'])
            _dir = Item(self['_'])
            _dir.collapse()
            return self.redirect('/browser?_=' + _dir.unipath.parent)
        return super(CollapseDirView, self).main()

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
            old_name = self['old_name']
            new_name = self['new_name']
            if new_name==old_name:
                report('nothing to do')
            else:
                is_dir = isdir(old_name)
                qs = self.get_queryset()
                shutil.move(old_name, new_name)
                report(str(['fs-move\n  ',old_name,'  ',new_name]))
                for item in qs:
                    new_path = item.path.replace(old_name, new_name)
                    report(str(['move-db\n  ',item.path,'  ',new_path]))
                    item.path = new_path
                    item.save()
                if is_dir:
                    return self.redirect('/browser?_=' + new_name)
                else:
                    return self.redirect(item.detail_url())
        return super(RenameView, self).main()
