""" ixle.views
"""
from flask import flash, redirect

from report import report
from ixle.views.search import ItemListView
from corkscrew.views import Favicon, BluePrint
from corkscrew.auth import Login, Logout
from corkscrew.util import use_local_template
from corkscrew.views import ListViews, SettingsView
from corkscrew.comet import SijaxDemo as CometDemo

from ixle.schema import Item, Event
from ixle.python import ope, isdir
from ixle.util import FSPath

from .base import View
from .search import Search
from .widgets import DirViewWidget, IsAvailable, Widget
from .agents import AgentView
from .spawn import Spawn
from .detail import Detail
from .browser import Browser
from .dsettings import SettingsView#NIY
from .home import HomePage

from .events import Events
from .nav import Nav
from ixle.views.api import APIView
from ixle.views.remotes import RemotesView
from ixle.views.newest import Newest
from ixle.views.fill import FillView
from ixle.views.rename import RenameView, CollapseDirView
from ixle.views.repackage import RepackageView
from .meta import _DB

class Suggest(View):
    url = '/suggest'
    template = 'suggest_name.html'

    def main(self):
        splits = '- .'
        suggestions = []
        return self.render(suggestions=suggestions)

class Delete(ItemListView):
    blueprint = BluePrint('asdasdas','asdasdasd')
    url = '/delete'
    template = 'delete.html'
    methods = 'get post'.split()

    def get_ctx(self, *args, **kargs):
        original = super(Delete, self).get_ctx(*args, **kargs)
        result = original.copy()
        result.update(
            is_dir = isdir(self['_']),)
        is_dir = isdir(self['_'])
        num_fs_files = 1 if not is_dir else len(FSPath(self['_']).listdir())
        num_db_files = 1 if not is_dir else len(Item.startswith(self['_']))
        result.update(
            confirmed=self['confirmed'],
            _=self['_'],
            num_db_files=num_db_files,
            num_fs_files=num_fs_files,
            is_dir = 1 if is_dir else 0,
            )
        _from = self['_from']
        opts = 'fs db both'
        opts = opts.split()
        assert _from in opts, 'must specify either fs, db, or both'
        result.update({'_from':_from,})
        result.update(info = dict( [[x,str(y)] for x,y in result.items() if x not in original]))
        return result

    def get_queryset(self):
        q = self['_']
        assert ope(q)
        if isdir(q):
            result = Item.startswith(q)
        else:
            result = Item.objects.filter(path=q)
        return result

    def delete_dir(self, path):
        ctx = self.get_ctx()
        _from = ctx['_from']
        assert ctx['num_fs_files']==0, 'can only remove empty dirs currently'
        if _from in 'both db'.split():
            for item in ctx['items']:
                report("removing from db: ",item)
                item.delete()
        if _from in 'both fs'.split():
            import os
            report('removing (empty) dir',self['_'])
            os.rmdir(self['_'])

    def main(self):
        ctx = self.get_ctx()
        if ctx['confirmed']:
            assert ctx['num_fs_files'] < 2,'multideletes disallowed currently'
            if ctx['is_dir']:
                self.delete_dir(self['_'])
                return self.redirect('/browser?_=' + FSPath(self['_']).parent)
        return super(Delete, self).main()

def generate_attribute_filter_view(ATTR_NAME, label='stuff'):
    """ """
    from ixle.views.search import ItemListView
    class GenericFiltrationView(ItemListView):
        #FIXME: inefficient, not paged..
        def get_queryset(self):
            out = Item.objects.filter(
                    **{self.ATTR_NAME:self['_']}) if self['_'] \
                    else []
            return out

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
from ixle.views.api import APIC
from ixle.views.hx import Hx
from ixle.views.file_viewer import Viewer
from ixle.views.dsettings import AppendSetting

__views__ = [
    # corkscrew standard views
    ListViews, Favicon, Login, Logout,
    APIC,

    #CometDemo,
    Hx, Viewer,

    #main ixle views
    SettingsView, AppendSetting,
    FillView,
    AgentView, Spawn, Browser,
    Search, Newest,
    HomePage,

    # views modifying the fs
    CollapseDirView, RenameView, RepackageView,

    FileTypeView, Fext, Detail, Events, MovieView,
    RemotesView,
    _DB,

    # ajax slaves or simple redirection views
    APIView, Delete, Nav, DirViewWidget, IsAvailable,
    ]
