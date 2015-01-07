""" ixle.views.repackage

    This view moves "FS siblings", or related files in
    the same directory, into a common directory.  The
    siblings themselves are guessed at by a heuristic
    (see also: ixle.heuristics.siblings)
"""
from report import report

from ixle.schema import Item
from ixle.python import mkdir, ope, opj
from ixle.views.search import ItemListView

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
                    item.move(new_path)
                    #shutil.move(item.path, new_path)
                    #item.path = new_path
                    #item.save()
            return self.redirect('/browser?_='+new_dir)
