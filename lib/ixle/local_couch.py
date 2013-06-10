""" ixle.local_couch

    Abstraction representing this application's
    (self-hosted) couchdb instance
"""
import tempfile
import sys
import os
import base64
import demjson
import shutil
import requests

from ixle.settings import Settings
from ixle.python import ope, opj
from glob import glob
from ixle.metadata import IxleMetadata, metadata

db_postfixes = ['',          # main database, do not remove!
                '_settings', # dynamic settings database
                '_events'    # events and suggestions
                ]

class CouchDB(object):

    @staticmethod
    def start_daemon():
        # TODO: allow local_ini override with -c option
        local_ini = IxleMetadata.default_local_ini
        if not ope(local_ini):
            error = 'Directory should exist: ' + local_ini
            return error
        else:
            override_ini = tempfile.mktemp(suffix='.ini')
            path2couchpy = opj(sys.prefix, #assumes venv?
                                'bin','couchpy')
            assert ope(path2couchpy)
            metadata.couch_settings['query_servers']['python'] = path2couchpy
            metadata.couch_settings['httpd']['port'] = Settings()['couch']['port']

            with open(override_ini,'w') as fhandle:
                metadata.couch_settings.write(fhandle)
            couch_cmd = 'couchdb -n -a {0}'.format(override_ini)
            assert os.path.exists('./cdb')
            print '--> running', couch_cmd
            return os.system(couch_cmd)

    @staticmethod
    def clean_data():
        """ remove the couchdb data and start over
            careful, because this kills *everything*:
              1) ixle user,
              2) ixle database,
              3) any other databases!
        """
        def get_data_files(ddir):
            return glob(opj(ddir, '*.couch'))

        def really_clean_data(dfiles):
            for _file in dfiles:
                print '  * removing ',_file
                os.remove(_file)
            print 'done'

        def reset_local_dot_ini():
            # changing the user database actually changes this file in-place.  if
            # "ixle --install" expects to add that the user back,
            #   we have to redact any
            # changes that were made there.
            print 'copying "{0}" -> "{1}"'.format(
                IxleMetadata.virgin_local_ini,
                IxleMetadata.default_local_ini)
            shutil.copy(IxleMetadata.virgin_local_ini,
                        IxleMetadata.default_local_ini)

        data_dir = './cdb'
        data_files = get_data_files(data_dir)
        reset_local_dot_ini()
        if ope(data_dir) and data_files:
            print 'this will remove these data files from "{0}":\n  {1}'.format(
                data_dir, data_files)
            answer = None
            while answer not in 'y n yes no'.split():
                answer = raw_input('are you sure? ')
            if answer in 'y yes'.split():
                really_clean_data(data_files)
        else:
            if not data_dir:
                error = 'data dir "0" does not exist'.format(data_dir)
            elif not data_files:
                error = 'no data files found in {0}.'.format(data_dir)
            return error

    @staticmethod
    def install_ixle(settings):
        """ run this after cleaning, and at the same time as --daemon
            (daemon has to be running or you can't add the users, duh)
        """
        def doit(earl, auth=None, data=None):
            print ' putting ', earl, ('with-auth' if auth else 'no-auth')
            r = requests.put(earl, data=data, auth=auth)
            hdrs=r.headers['content-type']
            stuff = r.status_code, demjson.decode(r.content)
            print ' -->', stuff
            return stuff

        def add_admin(data):
            earl = '{host}/_config/admins/{user}'.format(host=host, user=user)
            return doit(earl, data=data)

        def add_db(db_name, auth=[]):
            earl = '{host}/{db_name}'.format(host=host, db_name=db_name)
            return doit(earl, auth=auth)

        host, db_name, user, password, port = [
            settings['couch.server'],
            settings['ixle.db_name'],
            settings['couch.username'],
            base64.b64decode(settings['couch.password']),
            settings['couch.port'],]
        host = host[:-1] if host.endswith('/') else host

        code, content = add_admin(password)
        if content.get('error', None) == 'unauthorized':
            print ' ----> already have an admin.. adjusting auth creds\n'
            auth = (user, password)
        else:
            auth = None

        for db_postfix in db_postfixes:
            this_db_name = db_name + db_postfix
            code, content = add_db(this_db_name, auth=auth)
            if content.get('error', None)=='file_exists':
                print ' ----> already have database@'+this_db_name
                print
        print ' finished setting up couch.'
