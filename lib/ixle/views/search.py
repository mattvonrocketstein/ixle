""" ixle.views.search """

from .base import View
from corkscrew.views import BluePrint
from report import report
from ixle.query import javascript
from ixle.schema import Item

page_size = 15

class Search(View):

    template = 'search.html'
    url = '/search'

    def get_couch_query(self,search_query):
        return javascript.key_search(search_query)

    @property
    def ajax(self):
        return self['ajax']

    def get_ctx(self):
        search_query = self['_']
        page = int(self['p'] or 1)
        start = 0
        end = page_size
        num_results = 0
        if self.ajax and search_query:
            couch_query = self.get_couch_query(search_query)
            start = page_size*(page-1)
            end   = page_size * page
            keys = (self.db%couch_query)[ start : end ]
            num_results = len(keys)
            items = [ Item.load(self.db, k) for k in keys ]
        else:
            items = None
        return dict(p=page, is_dir='',
                    num_results=num_results,
                    query=search_query, items=items,
                    start=start, end=end)

    def main(self):
        ctx = self.get_ctx()
        if not self.ajax:
            return self.render(**ctx)
        else:
            return self.flask.render_template('item_list_raw.html', **ctx)
