""" ixle.views.search """

from .base import View
from corkscrew.views import BluePrint
from report import report
from ixle.util import javascript
from ixle.schema import Item

page_size = 15

class Search(View):

    template = 'search.html'
    url = '/search'

    def get_couch_query(self,search_query):
        return javascript.key_search(search_query)

    def get_ctx(self):
        search_query = self['_']
        report('query is: ',search_query)
        page = int(self['p'] or 1)
        start = 0
        end = page_size
        num_results = 0
        if search_query:
            couch_query = self.get_couch_query(search_query)
            start = page_size*(page-1)
            end   = page_size * page
            keys = (self.db%couch_query)[ start : end ]
            num_results = len(keys)
            items = [Item.load(self.db,k) for k in keys]
        else:
            items = []
        return dict(p=page,
                    num_results=num_results,
                    query=search_query, items=items,
                    start=start, end=end)

    def main(self):
        return self.render(**self.get_ctx())

class Browser(Search):

    blueprint = BluePrint(__name__, __name__)
    url = '/browser'
    template = 'browser.html'

    def get_ctx(self):
        import os
        from ixle.python import ope, opj
        from ixle.agents import registry
        ctx = super(Browser, self).get_ctx()
        qstring = self['_']
        if ope(qstring): # should be a dir already..
            subddirs=[ [x,opj(qstring,x)] for x in os.listdir(qstring)]
            subddirs = filter(lambda x: os.path.isdir(x[1]), subddirs)
        else:
            subddirs=[]
        ctx.update(subddirs=subddirs,
                   agent_types = registry.keys())
        return ctx

    def get_couch_query(self, search_query):
        return javascript.key_startswith(search_query)
