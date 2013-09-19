""" ixle.engine._mongo
"""

import mongoengine
import configparser
from pymongo import MongoClient
import os
from ixle.util import report
from .base import Engine

MYCP = configparser.ConfigParser
class MongoDatabaseWrapper(object):
    def __init__(self,old):
        self.old = old
    def __iter__(self):
        return self.old.find()

class MongoClientWrapper(object):
    def __init__(self,old):
        self.old=old
    def create(self,db_name):
        return self.old[db_name]
    def __getitem__(self,name):
        return MongoDatabaseWrapper(self.old[name])

    def edit_url(self, db):
        return '#edit_url-{0}'.format(db)

    def document_url(self, db_name, doc_id):
        return '#doc_url-{0}-{1}'.format(db_name, doc_id)

    def admin_url(self, db_name):
        return '#admin_url-{0}'.format(db_name)

    def __contains__(self, other):
        assert isinstance(other, basestring)
        return other in self.old.collection_names()
#raise Exception#def __iter__(self):
        #from ixle.schema import Item
        #return Item.objects.all()

class MongoDB(Engine):
    server_cmd = 'mongod --config {0}'

    def get_database(self):
        self.get_server()
        from ixle.schema import Item
        return Item.objects

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
        port = int(self.settings['mongo']['port'])
        host = self.settings['mongo']['host']
        mongoengine.connect(self['ixle']['db_name'],
                            host=host,
                            port=port)
        return MongoClientWrapper(
            getattr(MongoClient(host, port),
                    self['ixle']['db_name']))
