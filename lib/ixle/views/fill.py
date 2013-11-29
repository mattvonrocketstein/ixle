""" ixle.views.fill
"""

from ixle.views.search import ItemListView

from report import report
from ixle.schema import Item
from ixle.views.search import ItemListView
from .base import View

class FillView(View):

    template = 'fill.html'
    url = '/fill'
    methods = 'get post'.upper().split()

    def main(self):
        from ixle.agents import registry
        registry = [ [name, kls] for name,kls in registry.items() if \
                     getattr(kls,'covers_fields',[])]
        registry=dict(registry)
        return self.render(agents=registry)
