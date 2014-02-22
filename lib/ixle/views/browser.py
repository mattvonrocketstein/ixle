""" ixle.views.browser
"""
import os
from ixle.python import ope, opj
from ixle.agents import registry
from ixle.views.search import Search
from corkscrew.views import BluePrint
from report import report
from ixle.schema import Item
from ixle.python import expanduser

class Browser(Search):

    #blueprint = BluePrint(__name__, __name__)
    url = '/browser'
    template = 'browser.html'

    def get_queryset(self):
        """ query for db items that start with the
            path given to the browser (_), but if a
            search query (q) is provided, filter based
            on that also
        """
        path = self['_']
        q = self['q']
        tmp = Item.startswith(path)
        if q:
            tmp = tmp.filter(__raw__={'path' : {'$regex':q}})
        return tmp

    def main(self):
        if not self['_']:
            return self.redirect(self.url+'?_=~')
        else:
            return super(Browser, self).main()

    def get_ctx(self):
        ctx = super(Browser, self).get_ctx()
        qstring = self['_']
        if not qstring:
            qstring='~'
        if qstring.startswith('~'):
            return self.redirect(self.url+'?_='+expanduser(qstring))
        if ope(qstring): # should be a dir already..
            contents = [ [x, opj(qstring,x)] for x in os.listdir(qstring)]
        else:
            contents = []
        subddirs = filter(lambda x: os.path.isdir(x[1]), contents)
        files = dict([x for x in contents if os.path.isfile(x[1])])
        ctx.update(subddirs=subddirs,
                   is_dir='yes', files=files,
                   agents = registry.keys())
        return ctx
