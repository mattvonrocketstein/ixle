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
                raise Exception,'niy'
            else:
                items = Item.objects.filter(
                    **{self.ATTR_NAME:field_query})
            return self.render(label=self.label,
                               **self.get_ctx()
                               #items=items,
                               #query=field_query,
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


class MyStdout(object):
    registry = {}
    def __init__(self, stdout):
        self.stdout = stdout

    def __getattr__(self, x): return getattr(self.stdout, x)

    def write(self, data):
        this = threading.current_thread()
        if this in self.registry:
            self.registry[this].put(data)
        else:
            self.stdout.write(data)

import time
import sys, threading
from Queue import Queue, Empty
class Chat(SijaxView):

    url = '/chat'
    template = "chat.html"

    def comet_do_work_handler(self, obj_response, sleep_time):
        def f():
            from ixle.api import indexer
            indexer('/home/vagrant/code/ixle/')
        fake = MyStdout(sys.stdout)
        t = threading.Thread(target=f, name='testing')
        q = Queue()
        fake.registry[t] = q
        sys.stdout = fake
        t.start()
        nothing_written = 0
        while t.is_alive():
            try: zult = q.get(block=False)
            except Empty: zult = ""
            if zult.strip():
                from ansi2html import Ansi2HTMLConverter
                conv = Ansi2HTMLConverter()
                zult = conv.convert(zult)
                obj_response.html_append('#progress', zult)
            else:
                nothing_written += 1
                if nothing_written > 3:
                    obj_response.html_append('#progress', '...')
                    yield obj_response
                    nothing_written = 0
            yield obj_response
            time.sleep(.5)

    def main(self):
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        if self.is_sijax:
            # The request looks like a valid Sijax request
            # Let's register the handlers and tell Sijax to process it
            self.sijax.register_comet_callback('do_work', self.comet_do_work_handler)
            out = self.sijax.process_request()
            return out
        return self.render()


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
