""" ixle.bin._ixle

    for help, use "ixle --help"

"""
import shutil
import base64
import os, sys
from glob import glob

import requests, demjson
from report import report

from ixle.settings import Settings
from ixle.python import opj, ope, dirname, abspath
dupes_postfix = '_dupes'

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

        for db_postfix in ['', dupes_postfix]:
            this_db_name = db_name + db_postfix
            code, content = add_db(this_db_name, auth=auth)
            if content.get('error', None)=='file_exists':
                print ' ----> already have database@'+this_db_name
                print
        print ' finished setting up couch.'

def entry():
    """ entry point from commandline """
    settings = Settings()
    opts, clargs = settings.get_parser().parse_args()
    action, args, kargs = None, tuple(), dict()
    if clargs:
        assert len(clargs)==1, 'only know how to parse one clarg'
        path = abspath(clargs.pop())
    else:
        path = None
    if opts.daemon: sys.exit(CouchDB.start_daemon())
    elif opts.clean: sys.exit(CouchDB.clean_data())
    elif opts.install: sys.exit(CouchDB.install_ixle(settings))
    elif opts.api:
        import unipath
        from ixle import api
        api_method = getattr(api,opts.api)
        assert settings.app;
        assert path,'api commands operate on paths'
        path = unipath.path.Path(path)
        sys.exit(api_method(path))

    elif opts.action:
        assert settings.app # implicit creation
        action = opts.action
        kargs = dict(path=path, settings=settings, fill=opts.fill)
        kargs.update(**opts.__dict__)
        FORBIDDEN='daemon encode clean runner install shell port'.split()
        [ kargs.pop(x) for x in FORBIDDEN]
        from ixle.agents import registry as _map
        try:
            kls = _map[action]
        except KeyError:
            report('no such action "{0}"'.format(action))
            report('available agents are: '+str(_map.keys()))
            suggestions = [k for k in _map if k.startswith(action)]
            if suggestions:
                report('')
                report(' maybe try these: '+str(suggestions))
        else:
            agent = kls(*args, **kargs)
            report('action/agent = ' + str([action, agent])+'\n')
            report('  w/ kargs=' + str(kargs))
            sys.exit(agent())
    else:
        # do whatever corkscrew would have done
        # (this makes sure that --shell still works)
       settings.run()
