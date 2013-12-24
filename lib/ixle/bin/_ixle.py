""" ixle.bin._ixle

    for help, use "ixle --help"

"""
import shutil
import tempfile
import base64
import os, sys
from glob import glob

import requests, demjson
from report import report

from ixle.metadata import metadata
from ixle.settings import Settings
from ixle.metadata import IxleMetadata
from ixle.python import opj, ope, dirname, abspath
from ixle.metadata import IxleMetadata

def entry():
    """ entry point from commandline """
    settings = Settings()
    engine = settings._engine
    opts, clargs = settings.get_parser().parse_args()
    action, args, kargs = None, tuple(), dict()
    settings.quiet = opts.quiet
    if clargs:
        assert len(clargs)==1, 'only know how to parse one clarg'
        path = abspath(clargs.pop())
    else:
        path = None
    if opts.self_test:
        # call tox programmatically, here
        sys.exit(NotImplementedError)
    elif opts.daemon: sys.exit(engine.start_daemon())
    elif opts.purge: sys.exit(engine.purge_data())
    #elif opts.install: sys.exit(engine.install())
    elif opts.api:
        import unipath
        from ixle import api
        api_method = getattr(api, opts.api)
        assert settings.app;
        assert path, 'api commands operate on paths'
        path = unipath.path.Path(path)
        sys.exit(api_method(path))

    elif opts.action:
        assert settings.app # implicit creation
        action = opts.action
        kargs = dict(path=path, settings=settings, fill=opts.fill)
        kargs.update(**opts.__dict__)
        FORBIDDEN = 'daemon encode purge runner install shell port'.split()
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
            results=agent()
            sys.exit()
    else:
        # do whatever corkscrew would have done
        # (this makes sure that --shell still works)
       settings.run()
