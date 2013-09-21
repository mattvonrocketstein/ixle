"""ixle.views.browser
"""
from ixle.views.search import Search
from corkscrew.views import BluePrint
from report import report
#from ixle.query import javascript
from ixle.schema import Item

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
            contents = [ [x, opj(qstring,x)] for x in os.listdir(qstring)]

        else:
            contents = []
        subddirs = filter(lambda x: os.path.isdir(x[1]), contents)
        files = dict([x for x in contents if os.path.isfile(x[1])])

        ctx.update(subddirs=subddirs,
                   is_dir='yes', files=files,
                   agent_types = registry.keys())
        return ctx

    def get_couch_query(self, search_query):
        return javascript.key_startswith(search_query)
