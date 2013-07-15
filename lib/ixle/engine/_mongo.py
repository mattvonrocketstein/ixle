""" ixle.engine._mongo
"""

import configparser
from pymongo import MongoClient
import os
from ixle.util import report
from .base import Engine

MYCP = configparser.ConfigParser
class DBWrapper(object):
    def __init__(self, name, real_db):
        self._name=name
        self._db = real_db
        self._collection = getattr(self._db, self._name)

    def __iter__(self):
        return self._collection.find()

class MongoDB(Engine):
    server_cmd = 'mongod --config {0}'

    def _create_main_database(self, main_db_name):
        return DBWrapper(
            main_db_name,
            getattr(self.get_server(), main_db_name))

    #def get_database(self)
    def _read_engine_settings(self):
        """ HACK:
              super's version only works for standard .ini files,
              this override is here because .conf is very close to
              .ini, as long as we install a fake section at the top..
        """
        cp = MYCP()
        with open(self.metadata.default_local_ini,'r') as fhandle:
            contents = unicode(u'[mongo]\n' + fhandle.read())
            cp.read_string(contents)
        self._cp_engine_settings = cp
        return cp

    def start_daemon(self):
        # TODO: allow local_ini override with -c option
        override_ini = self._get_tmp('conf')
        tmp = self.engine_settings#['dbpath'] = '...'#path2couchpy
        tmp['mongo']['dbpath'] = os.path.sep.join(
            [ self.settings['ixle']['data_dir'],
            'data.mongo'])
        tmp['mongo']['logpath'] = os.path.sep.join(
            [ self.settings['ixle']['data_dir'],
            'mongo.log'])
        tmp['mongo']['bind_ip'] = self.settings['mongo']['host']
        rewritten = ['{0}={1}'.format(k,v) for k,v in tmp['mongo'].items() ]

        with open(override_ini, 'w') as fhandle:
                fhandle.write('\n'.join(rewritten))
                report('rewrote config to: ' + override_ini)
        cmd = self.server_cmd.format(override_ini)
        self._start_daemon(cmd)

    def get_server(self):
        return MongoClient(self.settings['mongo']['host'],
                           int(self.settings['mongo']['port']))
