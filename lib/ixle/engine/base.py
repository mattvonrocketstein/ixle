""" ixle.engine.base
"""
import os
from ixle.python import ope
from ixle.util import report

class Engine(object):
    def __init__(self):
        from ixle.settings import Settings
        from ixle.metadata import metadata
        self.settings = Settings()
        self.metadata = metadata

        local_ini = self.metadata.default_local_ini
        if not ope(local_ini):
            error = 'Directory should exist: ' + local_ini
            raise SystemExit(error)

    def _get_tmp_ini(self): # TODO: deprecate
        return self._get_tmp('ini')

    def _get_tmp(self,s):
        import tempfile
        s = '.'+s if not s.startswith('.') else s
        return tempfile.mktemp(suffix=s)

    def __getitem__(self, name):
        return self.settings[name]

    @property
    def engine_settings(self):
        import configparser
        if getattr(self, '_cp_engine_settings', None):
            return self._cp_engine_settings
        else:
            return self._read_engine_settings()

    def _read_engine_settings(self):
        """ works for standard .ini files """
        cp = configparser.ConfigParser()
        cp.read(self.metadata.default_local_ini)
        self._cp_engine_settings = cp
        return cp

    def _start_daemon(self, cmd):
        daemon_data_dir = self.settings['ixle']['data_dir']
        if not ope(daemon_data_dir):
            report("settings[ixle][data_dir] does not exist; creating it.")
            os.mkdir(daemon_data_dir)
        print '--> running', cmd
        return os.system(cmd)


    # TODO: honor name and use for secondary stuff
    def get_database(self, name=None):
        db = getattr(self, '_database', None)
        if db is None:
            db = self._get_or_create_database()
        return db
    def _get_or_create_database(self, name=None):
        """ this can either create the main database
            or create a connection to it.  the
            (see also: the `database` property handles
            caching the database and it's connection locally)
        """
        main_db_name = name or self['ixle']['db_name']
        import socket
        try:
            db = self._create_main_database(main_db_name)
        except socket.error, e:
            raise RuntimeError('is the internet turned on? originally: '+str(e))
        self._db = db
        return db
