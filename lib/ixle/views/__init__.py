""" ixle.views
"""
from flask import flash, redirect

from report import report

from corkscrew.views import Favicon, BluePrint
from corkscrew.auth import Login, Logout
from corkscrew.util import use_local_template
from corkscrew.views import ListViews, SettingsView, SijaxView

from ixle.schema import Item, Event

from .base import View
from .search import Search
from .widgets import DirViewWidget, IsAvailable, Widget
from .agents import AgentView
from .spawn import Spawn
from .detail import Detail
from .browser import Browser
from .dsettings import SettingsView#NIY
from .home import HomePage

from corkscrew.views import SijaxView
from .events import Events
from .nav import Nav
from ixle.views.api import APIView
from ixle.views.remotes import RemotesView
from ixle.views.newest import Newest
from ixle.views.fill import FillView
from ixle.views.rename import RenameView


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
            dbs = [])# self.wrapper(x) for x in self.settings.server])

class Suggest(View):
    url = '/suggest'
    template = 'suggest_name.html'

    def main(self):
        splits = '- .'
        suggestions = []
        return self.render(suggestions=suggestions)

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
    from ixle.views.search import ItemListView
    class GenericFiltrationView(ItemListView):
        #FIXME: inefficient, not paged..
        def get_queryset(self):
            assert self['_']
            return Item.objects.filter(
                    **{self.ATTR_NAME:self['_']})

        def filter(self):
            from ixle.schema import Item
            # something like "avi"
            field_query = self['_']
            # both cases return a <Row>-iterator
            if field_query == 'None':
                raise Exception, 'niy'
            else:
                items = Item.objects.filter(
                    **{self.ATTR_NAME:field_query})
            return self.render(label=self.label,
                               **self.get_ctx()
                               )

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
FileTypeView  = generate_attribute_filter_view('file_type', label='types')
MovieView  = generate_attribute_filter_view('is_movie', label='is_movie')

import time
import sys, threading
from Queue import Queue, Empty
from goulash.stdout import ThreadedStdout
from goulash.ansi import Ansi2HTMLConverter

fake = ThreadedStdout(sys.stdout)
fake.install()


class Chat(SijaxView):

    url = '/chat'
    template = "chat.html"
    extra_scripts=[ '/static/js/sijax/sijax.js',
                    '/static/js/sijax/sijax_comet.js' ]

    def worker(self):
        #from ixle.api import indexer
        #indexer('/home/vagrant/code/ixle/')
        import time
        self.report('stuff')
        print 1; time.sleep(1)
        print 2; time.sleep(2)
        print 3; time.sleep(1)
        print 4; time.sleep(2)
        report("print 5; time.sleep(2)")
        report("print 6; time.sleep(2)")
        print 7;
        print 4;

    def comet_handler(self, obj_response):
        """ """
        conv = Ansi2HTMLConverter(inline=False, escaped=False)
        unansi = conv.convert
        obj_response.html_append('#comet_data', conv.get_style())
        thr = threading.Thread(target=self.worker, name='testing')
        q = fake.register(thr)
        thr.start()

        hidebusy = lambda:obj_response.css('#loading_icon', 'display', 'none')
        showbusy = lambda:obj_response.css('#loading_icon', 'display', 'block')

        def read():
            zult = fake.read_all(thr).replace('\n','<br/>')
            if zult:
                zult = unansi(zult)
                obj_response.html_append('#comet_data', zult)
                hidebusy()
            else:
                showbusy()

        while thr.is_alive():
            read()
            yield obj_response
            time.sleep(.5)
        read()
        hidebusy()
        yield obj_response

    def main(self):
        if self.is_sijax:
            self.sijax.register_comet_callback('do_work', self.comet_handler)
            out = self.sijax.process_request()
            return out
        return self.render(javascript=self.sijax.get_js())


__views__ = [
    # corkscrew standard views
    ListViews, Favicon, Login, Logout, Chat,

    #main ixle views
    SettingsView, FillView,
    AgentView, Spawn, Browser,
    Search, Newest,
    HomePage, RenameView,
    FileTypeView, Fext, Detail, Events, MovieView,
    RemotesView,
    _DB,

    # ajax slaves or simple redirection views
    APIView, Delete, Nav, DirViewWidget, IsAvailable,
    ]
