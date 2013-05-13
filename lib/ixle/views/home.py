"""ixle.views.home"""

from .base import View
from ixle.schema import Item

class HomePage(View):
    url = '/'
    template = 'item_list.html'

    def main(self):
        db = self.settings.database
        keys = [k for k in db]
        page=keys[:100]
        items = [Item.load(db, k) for k in page]
        return self.render(items=items)
