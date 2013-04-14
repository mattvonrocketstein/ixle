""" ixle.settings
"""

from corkscrew.settings import Settings as CorkscrewSettings

class Settings(CorkscrewSettings):

    default_file = 'ixle.ini'

    @property
    def ignore_globs(self):
        return [ x for x in self['ixle.ignore'].split(',') if x ]

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

    @property
    def database(self):
        db = getattr(self,'_database',None)
        if db is None:
            db = self.server[ self['ixle.db_name'] ]
            self._db = db
        return db

    @classmethod
    def get_parser(kls):
        parser = CorkscrewSettings.get_parser()
        parser.add_option('--install', dest='install',
                          default=False, action='store_true',
                          help='boostrap ixle into running couchdb')
        parser.add_option('--clean', dest='clean',
                          default=False, action='store_true',
                          help='clean couch data dir(DANGER!)')
        parser.add_option('--action', dest='action',default='',
                          help='action [index|stale|]')
        parser.add_option('--daemon',"-d", dest="daemon",
                          default=False, action='store_true',
                          help="start couch daemon")
        return parser
