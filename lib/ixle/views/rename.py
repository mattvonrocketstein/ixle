""" ixle.views.rename
"""
import shutil
from ixle.views.search import ItemListView

from report import report
from ixle.schema import Item
from ixle.python import isdir, ope
from ixle.views.search import ItemListView
from .base import View
#Item.startswith('/home/vagrant/host/Downloads/The Holy Mountain (Uncut').count()
#)')(1973) DVDRip (SiRiUs sHaRe)'
# z=55; print q[:z]; print Item.startswith(q[:z]).count()
# z=50; print q[:z]; print Item.startswith(q[:z]).count()

class RenameView(ItemListView):

    template = 'rename.html'
    url      = '/rename'
    methods  = 'get post'.upper().split()

    def get_ctx(self, *args, **kargs):
        result=super(RenameView,self).get_ctx(*args, **kargs)
        result.update(is_dir=isdir(self['_']))
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
                for item in qs:
                    item.path = item.path.replace(old_name, new_name)
                    item.save()
                if is_dir:
                    return self.redirect('/browser?_='+new_name)
                else:
                    return self.redirect(item.detail_url())
        return super(RenameView,self).main()
        #return self.render()
