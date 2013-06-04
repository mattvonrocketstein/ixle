""" ixle.api

    DEFINITIONS:

      api-methods operate on Item objects, and might have side-effects on the
      database or the filesystem.

      rather than doing some cumbersome registration procedure for api-methods,
      all api-methods will be mined out of this file based on whether they are
      callable and whether the first argument's name is "path".
"""
import unipath
from report import report
from ixle import util, query
from ixle.schema import Item
from ixle.util import database, conf

def call_agent(agent_nick, item):
    """ helper method for when you want to
        turn agents into api methods
    """
    from ixle.agents import registry
    kls = registry[agent_nick]
    class mymixin(object):
        def __iter__(self):
            return iter([[item.abspath, item]])
    kls = type('Dynamic_API_From_Agent',
               (mymixin, kls),
               {})
    agent = kls(path=item.id, settings=conf(), force=True,)
    result = agent()
    report('called agent, got ' + str(result))
    if result is None:
        print 'got None-result from agent, should have been self.record.'
    return agent, result

def build_agent_method(name):
    def fxn(path):
        item = path2item(path)
        if item is None:
            return dict(error='no item found: "{0}"'.format(path))
        agent, result = call_agent(name, item)
        if not result: result=agent.record
        return dict(result)
    fxn.__name__ = name
    return fxn

stale = build_agent_method('stale')
itagger = build_agent_method('itagger')
imdb = build_agent_method('imdb')
moviefinder = build_agent_method('moviefinder')
tagger = build_agent_method('tagger')
filer = build_agent_method('filer')
renamer = build_agent_method('renamer')
slayer = build_agent_method('slayer')

def _space_filename(item):
    i1 = item.fname
    agent, result = call_agent('spacekiller', item)
    #report_what_changed(item)
    i2 = item.fname
    return dict(
        changed_filename='"{0}" to "{1}"'.format(i1,i2))

def path2item(path):
    db = database()
    return Item.load(db, path)

def spacekiller(path):
    return _space_filename(path2item(path))

def typer(path):
    item=path2item(path)
    agent, result = call_agent('typer',item)
    return dict(status='ok')


def moviefinder(path):
    item = path2item(path)
    agent, result = call_agent('moviefinder', item)
    return dict(status='ok')

def kill_directory(directory):
    print 'this is killd'
    path = unipath.path.Path(directory)
    assert path.exists(),(
        'to kill it, the path needs to exist.  '
        'if you just want these items out of the database, '
        'use untrack_directory')
    assert path.isdir(),'input is not a directory.'
    count = 0
    for item in query.key_startswith(
        util.database(), d):
        print item
        count += 0
    return dict(docs_deleted=count,
                dirs_deleted=[d])
