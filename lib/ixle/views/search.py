""" ixle.views.search """

from .base import View
from report import report
from ixle.schema import Item

from ixle.pages import per_page, Pagination
from werkzeug.wrappers import Response


class ItemListView(View):

    @property
    def ajax(self):
        return self['ajax']

    def pagination_ctx(self, items):
        page = int(self['p'] or 1)
        pitems = Pagination(items, page, per_page)
        items = pitems.items
        num_results = pitems.total
        num_pages = pitems.pages
        return dict(page=page,
                    pagination=pitems,
                    num_results=num_results,
                    num_pages=num_pages,
                    items=items)

    def get_ctx(self, **kargs):
        search_query = self['_']
        result = dict(_ = search_query,
                      ajax = self.ajax,
                      query = search_query,)
        result.update(
            self.pagination_ctx(self.get_queryset()))
        return result

    def main(self):
        ctx = self.get_ctx()
        if isinstance(ctx, Response):
            # hack: might be a redirect instead of context
            return ctx
        if not self.ajax:
            return self.render(**ctx)
        else:
            return self.flask.render_template('item_list_raw.html', **ctx)

class Search(ItemListView):

    template = 'search.html'
    url      = '/search'
    methods  = 'get post'.upper().split()

    def get_queryset(self):
        return Item.contains(self['_'])
