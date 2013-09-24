""" ixle.views.search """

from .base import View
from corkscrew.views import BluePrint
from report import report
#from ixle.query import javascript
from ixle.schema import Item

from ixle.pages import per_page, Pagination

class Search(View):

    template = 'search.html'
    url = '/search'
    methods = 'get post'.upper().split()

    #def get_couch_query(self, search_query):
    #    return javascript.key_search(search_query)

    @property
    def ajax(self):
        return self['ajax']

    def get_ctx(self):
        search_query = self['_']
        page = int(self['p'] or 1)
        items = Item.contains(search_query)
        pitems = Pagination(items, page, per_page)
        items = pitems.items
        num_results = pitems.total
        num_pages = pitems.pages
        return dict(_=search_query,
                    pagination=pitems, is_dir='',
                    num_results=num_results,
                    query=search_query, items=items,
                    )

    def main(self):
        ctx = self.get_ctx()
        if not self.ajax:
            return self.render(**ctx)
        else:
            return self.flask.render_template('item_list_raw.html', **ctx)
