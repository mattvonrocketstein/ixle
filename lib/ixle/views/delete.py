""" ixle.views.delete
"""
import os
from ixle.python import ope, isdir
from report import report
from ixle.util import FSPath
from ixle.schema import Item
from ixle.views.search import ItemListView

class Delete(ItemListView):
    url = '/delete'
    template = 'delete.html'
    methods = 'get post'.split()

    def get_ctx(self, *args, **kargs):
        original = super(Delete, self).get_ctx(*args, **kargs)
        result = original.copy()
        fspath = FSPath(self['_'])
        is_dir = fspath.isdir()
        num_fs_files = 1 if not is_dir else len(fspath.listdir())
        num_db_files = 1 if not is_dir else len(Item.startswith(self['_']))
        result.update(
            confirmed=self['confirmed'],
            _ = self['_'],
            num_db_files=num_db_files,
            num_fs_files=num_fs_files,
            is_dir = 1 if is_dir else 0,
            )
        _from = self['_from']
        opts = 'fs db both'
        opts = opts.split()
        assert _from in opts, 'must specify either fs, db, or both'
        result.update({'_from':_from,})
        result.update(info = dict( [[x,str(y)] for x,y in result.items() if x not in original]))
        return result

    def get_queryset(self):
        q = self['_']
        assert ope(q)
        if isdir(q):
            result = Item.startswith(q)
        else:
            result = Item.objects.filter(path=q)
        return result

    def delete_dir(self, path):
        ctx = self.get_ctx()
        _from = ctx['_from']
        assert ctx['num_fs_files']==0, 'can only remove empty dirs currently'
        if _from in 'both db'.split():
            for item in ctx['items']:
                report("removing from db: ",item)
                item.delete()
        if _from in 'both fs'.split():
            report('removing (empty) dir',self['_'])
            os.rmdir(self['_']) # NOTE: throws OSError if not empty

    def delete_item(self, path):
        ctx = self.get_ctx()
        _from = ctx['_from']
        assert ctx['num_fs_files']==1, 'can only remove single files currently'
        assert ctx['num_db_files']==1, 'can only remove single files currently'
        if _from in 'both db'.split():
            item=ctx['items'][0]
            report("removing from db: ",item)
            item.delete()
        if _from in 'both fs'.split():
            report('removing file', self['_'])
            os.remove(self['_'])

    def main(self):
        ctx = self.get_ctx()
        if ctx['confirmed']:
            assert ctx['num_fs_files'] < 2,'multideletes disallowed currently'
            _ = self['_']
            if ctx['is_dir']:
                self.delete_dir(_)
                path = FSPath(self['_']).parent.parent # 2x because of trailing slash
                return self.redirect('/browser?_=' + path)
            else:
                self.delete_item(_)
                return self.redirect('/browser?_=' + FSPath(self['_']).parent)
        return super(Delete, self).main()

DeleteView = Delete
