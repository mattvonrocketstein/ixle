""" ixle.settings
"""
import couchdb
import warnings
from corkscrew.settings import Settings as CorkscrewSettings

import json
import humanize

def escapejs(val):
    try:
        out = json.dumps(str(val))
    except UnicodeEncodeError,e:
        print 'error decoding ',val
        out = val
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

        from flask import Blueprint
        from flask.ext.silk import Silk
        blu = Blueprint(__name__, __name__)
        silk = Silk(blu, silk_path='/icons/')

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
    def _engine(self):
        if hasattr(self, '_engine_'): return self._engine_
        else:
            import ixle.engine as engines
            engine_name = self['ixle']['engine']
            self._engine_ = getattr(engines, engine_name)
            return self._engine_

    @property
    def server(self):
        return self._engine.get_server()

    @property
    def database(self):
        return self._engine.get_database()

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
        parser.add_option('--purge', dest='purge',
                          default=False, action='store_true',
                          help='purge all data from engine(DANGER!)')
        parser.add_option('--action', dest='action',default='',
                          help='action [{0}]'.format(
                              '|'.join(registry.keys())))

        parser.add_option('--api', dest='api',default='',
                          help='api <cmd>'),
        parser.add_option('--daemon',"-d", dest="daemon",
                          default=False, action='store_true',
                          help="start couch daemon")
        parser.add_option('--test',"-t", dest="self_test",
                          default=False, action='store_true',
                          help="run self tests")
        return parser
