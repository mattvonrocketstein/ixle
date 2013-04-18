""" ixle.views
"""
import threading
from flask import flash, redirect

from report import report

from corkscrew.views import Favicon
from corkscrew.auth import Login, Logout
from corkscrew.util import use_local_template
from corkscrew.views import ListViews, SettingsView

from hammock.views.administration import CouchView

from ixle.schema import Item, DupeRecord
from ixle.util import find_equal, find_empty, rows2items
from ixle.agents import registry

from .base import View, BluePrint
from .search import Search, Browser
from .widgets import DirViewWidget

class Spawn(View):
    """ spawn agent on a given sandwich """
    url = '/spawn'
    blueprint = BluePrint(__name__, __name__)
    template = 'spawn.html'
    methods = "GET POST".split()
    def main(self):
        force = True if self['force'] else False
        agent = self['agent']
        path = self['path']
        if agent and path:
            try:
                kls = registry[agent]
            except KeyError:
                flash("Unknown agent")
                return self.render(path=path, agent='')
            kargs = dict(settings=self.settings,
                         path=path, force=force)
            agent = kls(**kargs)
            report('created agent type {0} with kargs={1}'.format(
                agent.__class__.__name__,
                str(kargs)))
            t = threading.Thread(target=agent)
            t.start()
            flash("started agent in thread; redirecting to browser")
            return redirect('/browser?_='+path)
        return self.render(path=path,
                           agent=agent)

#NIY
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

def generate_attribute_filter_view(ATTR_NAME, label='stuff'):
    """ """
    class GenericFiltrationView(View):
        #FIXME: inefficient, not paged..
        def filter(self):
            # something like "avi"
            fext_query = self['_']
            # both cases return a <Row>-iterator
            if fext_query=='None':
                fext_query = '(NULL)'
                items = find_empty(self.db, self.ATTR_NAME)
            else:
                items = find_equal(self.db, self.ATTR_NAME, fext_query)
                # get back a list of items
            items = [x for x in rows2items(self.db, items,
                                           approx=True)]
            return self.render(label=self.label,
                               items=items,
                               query=fext_query)

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
                     blueprint = BluePrint(ATTR_NAME + '_list',
                                           ATTR_NAME + '_list'),
                     template = 'filter_by_fext.html'))

Fext = generate_attribute_filter_view('fext', label='extensions')
FileTypeView  = generate_attribute_filter_view('file_type',label='types')

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
    CouchView, ListViews, SettingsView, Favicon, Login, Logout,

    #main ixle views
    Spawn, Browser, Search, X, FileTypeView, Fext, Detail, Dupes,

    # ajax slaves
    Nav, DirViewWidget,
    ]
