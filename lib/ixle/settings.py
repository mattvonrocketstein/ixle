""" ixle.settings
"""
import couchdb
from corkscrew.settings import Settings as CorkscrewSettings

import humanize

import json

def escapejs(val):
    out = json.dumps(str(val))
    return out

class DSettingsMixin(object):
    @property
    def _dynamic(self):
        if getattr(self,'_dsettings', None) is None:
            from ixle.dsettings import dynamic_settings
            self._dsettings = dynamic_settings()
        return self._dsettings

    @property
    def random_sample_size(self):
        tmp = self._dynamic['random_sample_size'].value or 10
        return int(tmp)


    @property
    def ignore_globs(self):
        """ pulls the 'ignore_patterns' setting out of couchdb """
        tmp = self._dynamic['ignore_patterns'].value or ''
        return [ x for x in tmp.split(',') if x ]

class Settings(CorkscrewSettings, DSettingsMixin):

    default_file = 'ixle.ini'

    env_filters = dict(
        # TODO: move this into corkscrew
        naturaltime=humanize.naturaltime,
        escapejs=escapejs)

    def __repr__(self):
        return '<ixle.settings.Settings>'

    def _get_app(self):
        app = super(Settings,self)._get_app()
        for name,fxn in self.env_filters.items():
            app.jinja_env.filters[name] = fxn
        return app

    def shell_namespace(self):
        """ the namespace published to ipython
            when using 'ixle --shell'
        """
        import re
        from couchdb.mapping import Document
        from ixle.schema import Item
        from ixle import util
        from ixle import heuristics
        #from ixle.fs import dbfs
        from ixle import agents
        from ixle import api
        from ixle import metadata
        return dict(re=re,
                    api=api,
                    agents=agents,
                    metadata=metadata.metadata,
                    util=util,
                    #dbfs=dbfs,
                    heuristics=heuristics,
                    item=Item, Item=Item,
                    #dupes_db=self.dupes_db,
                    database=self.database)

    @property
    def server(self):
        server = getattr(self, '_server', None)
        if server is None:
            # ugh, hack
            from hammock._couch import Server
            conf = type('conf', (object,), dict(settings=self))
            server = Server(conf)
            self._server = server
        return server

    def _create_main_database(self):
        main_db_name = self['ixle']['db_name']
        try:
            return self.server[ main_db_name  ]
        except couchdb.http.ResourceNotFound:
            from ixle.util import report
            raise RuntimeError("ResourceNotFound creating main database;"
                               " did you run 'ixle --install'?")

    @property
    def database(self):
        # TODO: abstract this caching pattern
        db = getattr(self, '_database', None)
        if db is None:
            db = self._create_main_database()
            self._db = db
        return db

    @property
    def events_db(self):
        # TODO: abstract this caching pattern
        from ixle.util import get_or_create
        db = get_or_create('ixle_events')
        return db

    @classmethod
    def get_parser(kls):
        from ixle.agents import registry
        parser = CorkscrewSettings.get_parser()
        parser.add_option('--force', dest='force', default=False,
                          action='store_true', help='force overwrite')
        parser.add_option('--fill', dest='fill', default=False,
                          action='store_true',
                          help=('query for entries '
                                'where FIELDNAME is not set'))
        parser.add_option('--install', dest='install',
                          default=False, action='store_true',
                          help='boostrap ixle into running couchdb')
        parser.add_option('--clean', dest='clean',
                          default=False, action='store_true',
                          help='clean couch data dir(DANGER!)')
        parser.add_option('--action', dest='action',default='',
                          help='action [{0}]'.format(
                              '|'.join(registry.keys())))

        parser.add_option('--api', dest='api',default='',
                          help='api <cmd>'),
        parser.add_option('--daemon',"-d", dest="daemon",
                          default=False, action='store_true',
                          help="start couch daemon")
        return parser
