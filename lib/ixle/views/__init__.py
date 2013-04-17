""" ixle.views
"""

from corkscrew.auth import Login, Logout
from corkscrew.views import Favicon, View,BluePrint
from corkscrew.util import use_local_template
from corkscrew.views import ListViews, SettingsView

from hammock.views.administration import CouchView
from ixle.schema import Item, DupeRecord
from ixle.util import find_equal, rows2items

from .base import View
from .search import Search

class Suggest(View):
    url = '/suggest'
    blueprint = BluePrint('suggest', __name__)
    template = 'suggest_name.html'

    def main(self):
        splits = '- .'
        suggestions = []
        return self.render(suggestions=suggestions)

class Dupes(View):
    url = '/dupes'
    blueprint = BluePrint('duples',__name__)
    template = 'dupes.html'
    def main(self):
        records = [ DupeRecord.load(self.dupes_db, k) \
                    for k in self.dupes_db.keys() ]
        return self.render(items=records)

class Nav(View):
    url = '/_nav'
    blueprint = BluePrint('nav', __name__)
    template = 'navigation.html'
    def main(self):
        return self.render()

class Detail(View):
    """ TODO: does not handle filenames with a '#' in them correctly """
    url = '/detail'
    blueprint = BluePrint('detail', __name__)
    template = 'item_detail.html'

    def main(self):
        k = self['_']
        item = Item.load(self.db, k)
        return self.render(item = item)

class Fext(View):
    url = '/fext'
    blueprint = BluePrint('fext_list', __name__)
    template = 'filter_by_fext.html'

    def filter(self):
        # something like "avi"
        fext_query = self['_']
        # returns a <Row>-iterator
        items = find_equal(self.db, 'fext', fext_query)
        # get back a list of items
        items = rows2items(self.db, items)
        return self.render(items=items, query=fext_query)

    @use_local_template
    def index(self):
        """
        {%for fext in fext_list%}
        <a href=?_={{fext}}>{{fext}}</a> |
        {%endfor%}
        """
        fext_list = self.db._unique_values_for_fieldname('fext')
        return dict(fext_list=fext_list)

    def main(self):
        if not self['_']: return self.index()
        else:
            fext = self['_']
            return self.filter()
class X(View):
    url = '/'
    blueprint = BluePrint('home', __name__)
    template = 'item_list.html'

    def main(self):
        db = self.settings.database
        keys = [k for k in db]
        page=keys[:100]
        items = [Item.load(db, k) for k in page]
        return self.render(items=items)

__views__= [
    # corkscrew standard views
    ListViews, SettingsView, Favicon, Login, Logout,
    Search, X, Nav, Fext, Detail, Dupes,
    CouchView, ]
