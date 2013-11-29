""" ixle.util
"""

import re, os
import datetime
import inspect
from itertools import imap

import pep362
from couchdb.client import ViewResults

from report import report
from ixle.python import ope
from ixle.schema import Item
from ixle._atexit import handle_exit

def field_name_to_agents(field_name):
    from ixle.agents import registry
    agents = registry.values()
    agents = [ a for a in agents if \
               field_name in getattr(a, 'covers_fields',[]) ]
    return agents

def field_name_to_agent(field_name):
    result = field_name_to_agents(field_name)
    err='only one agent should cover field "{0}", found {1}'
    assert len(result)==1,err.format(field_name, result)
    return result[0]

def agent_cover():
    """ returns { ItemFieldName: AgentWhichCoversIt}
    """
    fields = Item._fields.copy()
    for ignored in 'host id'.split(): fields.pop(ignored)
    out = [ [ fname,
              field_name_to_agent(fname)] \
            for fname in fields]
    out = dict(out)
    return out

    return out

def wrap_kbi(fxn):
    def cleanup():
        print "exiting.."
    def newf(*args, **kargs):
        with handle_exit(cleanup):
            fxn(*args, **kargs)
    return newf

def conf():
    from ixle import settings
    return settings.Settings()

def report_if_verbose(*args, **kargs):
    # TODO:
    pass

def get_or_create(DB_NAME):
    from ixle.settings import Settings
    server = Settings().server
    if DB_NAME not in server:
        report("creating database {0} on {1} ".format(DB_NAME, server))
        server.create(DB_NAME)
    db = server[DB_NAME]
    return db

def database():
    """ get a handle for the main database object """
    return conf().database

def _harvest(modyool, arg_pattern=None, test=None):
    """ retrieve functions from module iff they have
        exactly 1 argument and that argument==arg_pattern
    """
    if not test:
        def test(obj):
            if callable(obj) and inspect.isfunction(obj):
                func_sig = pep362.Signature(obj)
                parameter_dict = func_sig._parameters
                if arg_pattern is not None:
                    if all([len(parameter_dict)==1,
                            arg_pattern in parameter_dict]):
                        return True
                return True
    names = set(dir(modyool)) - set(dir(__builtins__))
    matches = []
    count=0
    for name in names:
        count+=1
        obj = getattr(modyool, name)
        if test(obj):
            matches.append(obj)
    return dict([m.__name__, m] for m in matches)

def call_agent_on_item(agent_nick, item):
    """ helper method for when you want to
        turn agents into api methods
    """
    kls = get_agent_by_name(agent_nick)
    class mymixin(object):
        def __iter__(self):
            # bypasses the normal query mechanism
            return iter([item])

    kls = type('Dynamic_API_From_Agent',
               (mymixin, kls),
               {})
    agent = kls(path=item.path, settings=conf(), force=True,)
    result = agent()
    report('called agent, got ' + str(result))
    if result is None:
        print 'got None-result from agent, should have been self.record.'
    return agent, result

def call_agent_on_dir(agent_nick, dirname):
    kls = get_agent_by_name(agent_nick)
    agent_obj = kls(path=dirname, settings=conf())
    result = agent()
    if result is None:
        raise Exception, ('got None-result from agent, '
                          'should have been self.record.')
    return agent, result

def get_api():
    from ixle import api
    d_action = _harvest(api, 'directory')
    p_action = _harvest(api, 'path')
    out = {}
    [ out.update(x) for x in [d_action, p_action] ]
    return out

def get_agent_by_name(name):
    from ixle.agents import registry
    return registry[name]

def get_heuristics():
    """ mines heuristic functions out of ixle.heuristics.
        that means: any simple function that takes one
        argument where that argument is named "item".

        returns a dictionary of { fxn_name : fxn }
    """
    from ixle import heuristics
    def is_heuristic(obj):
        return not getattr(obj,'__name__',None)=='Heuristic' and \
               getattr(obj, 'is_heuristic', False)
    return _harvest(heuristics, test=is_heuristic)

def modification_date(filename):
    """ """
    if ope(filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)
    else:
        pass #report('cant get mod_date: '+str(filename))

R_SPLIT_DELIM = re.compile('[\W_]+')
def smart_split(x):
    """ splits on most delims """
    return R_SPLIT_DELIM.split(x)

def no_alphabet(x):
    """ argh FIXME """
    no_delim = ''.join(smart_split(x))
    return len(no_delim) == re.compile('\d*').match(no_delim).end()
