""" ixle.views.search """

from .base import View
from corkscrew.views import BluePrint
from ixle.util import key_contains, rows2items, key_search

class Search(View):

    blueprint = BluePrint('search', __name__)
    template = 'search.html'
    url = '/search'

    def main(self):
        query = self['_']
        if query:
            items = rows2items(self.db, key_search(self.db, query))
        else:
            items=[]
        return self.render(query=query, items=items)
