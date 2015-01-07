""" ixle.views.hx
"""

from report import report

from ixle.schema import Item
from ixle.agents import registry
from ixle.views.base import View
from ixle.util import get_heuristics
from ixle.heuristics import run_heuristic

class Hx(View):
    url      = '/hx'
    template = 'item/heuristic.html'

    def main(self):
        item  = self.get_current_item()
        hname = self['hx']
        if not isinstance(item, Item): # not_found
            return item
        else:
            return self.render(
                item=item,
                heuristics=run_heuristic(hname, item))
