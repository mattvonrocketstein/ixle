""" ixle.views.detail
"""

from report import report

from ixle.schema import Item
from ixle.agents import registry
from ixle.views.base import View
from ixle.heuristics import run_heuristics

class ItemDetail(View):
    """ TODO: does not handle filenames with a '#' in them correctly """
    url = '/detail'
    template = 'item/detail.html'

    def get_ctx(self):
        item = self.get_current_item()
        return dict(
            query = self['_'],
            item=item,
            heuristics=run_heuristics(item))

    def main(self):
        item = self.get_current_item()
        if not isinstance(item, Item): # not_found
            return item

        # TODO: should be api command
        # check for any requests to set specific fields back to nil
        reset_requests = [ x[len('reset_'):] \
                           for x in self.request.values.keys() \
                           if x.startswith('reset_') ]
        if reset_requests:
            # TODO: do this with api
            raise Exception,'deprecated'

        from ixle.util import get_api
        return self.render(**self.get_ctx())
Detail=ItemDetail
