""" ixle.bin._ixle
"""
import shutil
import base64
import os, sys
from glob import glob
from report import report
from ixle.settings import Settings
from ixle.python import opj, ope, dirname, abspath
from ixle.agents import Md5er, Indexer, StaleChecker, Janitor, Sizer, Typer, Filer

class IxleMetadata:
    ixle_home = dirname(dirname(__file__))
    ixle_config = opj(ixle_home, 'config')
    default_local_ini = abspath(opj(ixle_config, 'local.ini'))
    virgin_local_ini = abspath(opj(ixle_config, 'local.ini.original'))

class CouchDB(object):
    @staticmethod
    def start_daemon():
        # TODO: allow local_ini override with -c option
        local_ini = IxleMetadata.default_local_ini
        if not ope(local_ini):
            error = 'Directory should exist: ' + local_ini
            return error
        else:
            couch_cmd = 'couchdb -n -a {0}'.format(local_ini)
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
            # "ixle --install" expects to add that the user back, we have to redact any
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
        def doit(string):
            print ' -> ',string
            os.system(string)
            print

        host, db_name, user, password, port = [
            settings['couch.server'],
            settings['ixle.db_name'],
            settings['couch.username'],
            base64.b64decode(settings['couch.password']),
            settings['couch.port'],]
        host = host[:-1] if host.endswith('/') else host
        add_database = 'curl -X PUT {host}/{db_name}'.format(
            host=host, db_name=db_name)
        add_database = add_database
        doit(add_database)
        add_admin = "curl -X PUT {host}/_config/admins/{user} -d '\"{password}\"'"
        add_admin = add_admin.format(host=host, password=password, user=user)
        doit(add_admin)

def run_index(path=None, settings=None, **kargs):
    indexer = Indexer(path=path, settings=settings)
    indexer.index()

def entry():
    """ entry point from commandline """
    settings = Settings()
    opts, clargs = settings.get_parser().parse_args()
    action, args, kargs = None, tuple(), dict()
    if clargs:
        assert len(clargs)==1, 'only know how to parse one clarg'
        path = clargs.pop()
    else:
        path = None
    if opts.daemon: sys.exit(CouchDB.start_daemon())
    elif opts.clean: sys.exit(CouchDB.clean_data())
    elif opts.install: sys.exit(CouchDB.install_ixle(settings))
    elif opts.action:
        action = opts.action
        kargs = dict(path=path, settings=settings)
        kargs.update(**opts.__dict__)
        _map = dict(md5=Md5er, typer=Typer,
                    filer=Filer,
                    sizer=Sizer, janitor=Janitor,
                    index=Indexer, stale=StaleChecker)
        kls = _map[action]
        agent = kls(*args, **kargs)
        report('action/agent', action, agent)
        sys.exit(agent())
    else:
        # do whatever corkscrew would have done
        # this makes sure that --shell still works
       settings.run()
