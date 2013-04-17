""" ixle.views.search """

from .base import View
from corkscrew.views import BluePrint
from ixle.util import javascript, key_contains, rows2items, key_search
from ixle.schema import Item
page_size = 100

class Search(View):

    blueprint = BluePrint('search', __name__)
    template = 'search.html'
    url = '/search'

    def main(self):
        search_query = self['_']
        page = int(self['p'] or 1)
        start = 0
        end = page_size
        num_results = 0
        if search_query:
            couch_query = javascript.key_search(search_query)
            start = page_size*(page-1)
            end   = page_size * page
            keys = (self.db%couch_query)[ start : end ]
            num_results = len(keys)
            items = [Item.load(self.db,k) for k in keys]
        else:
            items = []
        return self.render(num_results=num_results,
                           query=search_query, items=items,
                           start=start, end=end)
