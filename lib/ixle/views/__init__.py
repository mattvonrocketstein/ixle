""" ixle.views
"""
from flask import flash, redirect

from report import report

from corkscrew.views import Favicon, BluePrint
from corkscrew.auth import Login, Logout
from corkscrew.util import use_local_template
from corkscrew.views import ListViews, SettingsView

from ixle.schema import Item, Event
#from ixle.query import find_equal, find_empty

from .base import View
from .search import Search
from .widgets import DirViewWidget, IsAvailable, Widget
from .agents import AgentView
from .spawn import Spawn
from .detail import Detail
from .browser import Browser
from .dsettings import SettingsView#NIY
from .home import HomePage

class _DB(View):
    methods = 'GET POST'.split()
    url = '/_db'
    template = '_db.html'

    def wrapper(self,db):
        return type('asdads',
                    (object,),
                    dict(
                        name=db,
                        edit_url=self.settings.server.edit_url(db)))

    def main(self):
        db = None
        if self['_'] or self['size']:
            db = self.settings.server[ self['_'] or self['size'] ]
        if self['size']:
            size = len(db)
            return str(size)
        if self['compact']:
            db.compact()
            return 'compacted'
        return self.render(
            db=self.wrapper(db),
            db_name=self['_'],
            dbs = [ self.wrapper(x) for x in self.settings.server])

class Suggest(View):
    url = '/suggest'
    template = 'suggest_name.html'

    def main(self):
        splits = '- .'
        suggestions = []
        return self.render(suggestions=suggestions)
from .events import Events
from .nav import Nav

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
        return redirect('/detail?_' + key)


def generate_attribute_filter_view(ATTR_NAME, label='stuff'):
    """ """
    class GenericFiltrationView(View):
        #FIXME: inefficient, not paged..
        def filter(self):
            from ixle.schema import Item
            # something like "avi"
            field_query = self['_']
            # both cases return a <Row>-iterator
            if field_query == 'None':
                field_query = '(NULL)'
                items = find_empty(self.db, self.ATTR_NAME)
            else:
                items = Item.objects.filter(
                    **{self.ATTR_NAME:field_query})
            # get back a list of items
            #items = [Item.wrap(r.doc) for r in items]
            return self.render(label=self.label,
                               items=items,
                               query=field_query)

        @use_local_template
        def index(self):
            """
            {%for fext in fext_list%}
            <a href="?_={{fext}}">{{fext}}</a> |
            {%endfor%}
            """
            fext_list = self.db.distinct(field=self.ATTR_NAME)
            return dict(this_url=self.url,
                        label=self.label,
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
MovieView  = generate_attribute_filter_view('is_movie',label='is_movie')

from ixle.views.api import APIView
from ixle.views.remotes import RemotesView

__views__= [
    # corkscrew standard views
    ListViews, Favicon, Login, Logout,

    #main ixle views
    SettingsView,
    AgentView, Spawn, Browser, Search, HomePage,
    FileTypeView, Fext, Detail, Events, MovieView,
    RemotesView,
    _DB,

    # ajax slaves or simple redirection views
    APIView, Delete, Nav, DirViewWidget, IsAvailable,
    ]
