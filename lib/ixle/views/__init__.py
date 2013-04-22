""" ixle.views
"""
from report import report

from corkscrew.views import Favicon, BluePrint
from corkscrew.auth import Login, Logout
from corkscrew.util import use_local_template
from corkscrew.views import ListViews, SettingsView

from hammock.views.administration import CouchView

from ixle.schema import Item, DupeRecord
from ixle.query import find_equal, find_empty

from .base import View
from .search import Search, Browser
from .widgets import DirViewWidget
from .agents import AgentView
from .spawn import Spawn

#NIY
from flask import flash, redirect

class Suggest(View):
    url = '/suggest'
    template = 'suggest_name.html'

    def main(self):
        splits = '- .'
        suggestions = []
        return self.render(suggestions=suggestions)

class Dupes(View):
    url = '/dupes'
    template = 'dupes.html'
    def main(self):
        if self['clear_all']:
            self.dupes_db.delete_all()
        records = [ DupeRecord.load(self.dupes_db, k) \
                    for k in self.dupes_db.keys() ]
        return self.render(items=records)

class Nav(View):
    url = '/_nav'
    template = 'navigation.html'
    def main(self):
        return self.render()

class Delete(View):
    blueprint = BluePrint('asdasdas','asdasdasd')
    url = '/delete'

    def main(self):
        key = self['_']
        _from = self['from']
        assert key and _from, 'need both key and where to delete from'
        if _from=='db':
            try:
                del self.db[key]
            except Exception,e:
                flash("Error: "+str(e))
            else:
                flash('successfully deleted key from database.')
        else:
            flash("did nothing; i dont know what you mean.")
        return redirect('/detail?_'+key)

class Detail(View):
    """ TODO: does not handle filenames with a '#' in them correctly """
    url = '/detail'
    template = 'item_detail.html'

    def main(self):
        k = self['_']
        if not k:
            return self.flask.render_template('not_found.html')
        item = Item.load(self.db, k)
        if item is None:
            return self.flask.render_template('not_found.html')
        return self.render(item = item)

def generate_attribute_filter_view(ATTR_NAME, label='stuff'):
    """ """
    class GenericFiltrationView(View):
        #FIXME: inefficient, not paged..
        def filter(self):
            # something like "avi"
            field_query = self['_']
            # both cases return a <Row>-iterator
            if field_query=='None':
                field_query = '(NULL)'
                items = find_empty(self.db, self.ATTR_NAME)
            else:
                items = find_equal(self.db, self.ATTR_NAME, field_query)
                # get back a list of items
            #items = [Item.wrap(r.doc) for r in items]
            return self.render(label=self.label,
                               items=items,
                               query=field_query)

        @use_local_template
        def index(self):
            """
            {%for fext in fext_list%}
            <a href=?_={{fext}}>{{fext}}</a> |
            {%endfor%}
            """
            fext_list = self.db._unique_values_for_fieldname(self.ATTR_NAME)
            return dict(label=self.label,
                        fext_list=fext_list)

        def main(self):
            if not self['_']: return self.index()
            else:
                fext = self['_']
                return self.filter()

    return type('DynamicFilterView' + str(id(GenericFiltrationView)),
                (GenericFiltrationView,),
                dict(ATTR_NAME=ATTR_NAME,
                     label = label,
                     url = '/' + ATTR_NAME,
                     template = 'filter_by_fext.html'))

Fext = generate_attribute_filter_view('fext', label='extensions')
FileTypeView  = generate_attribute_filter_view('file_type',label='types')

class HomePage(View):
    url = '/'
    template = 'item_list.html'

    def main(self):
        db = self.settings.database
        keys = [k for k in db]
        page=keys[:100]
        items = [Item.load(db, k) for k in page]
        return self.render(items=items)

__views__= [
    # corkscrew standard views
    CouchView, ListViews, SettingsView, Favicon, Login, Logout,

    #main ixle views
    AgentView, Spawn, Browser, Search, HomePage,
    FileTypeView, Fext, Detail, Dupes,

    # ajax slaves or simple redirection views
    Delete, Nav, DirViewWidget,
    ]
