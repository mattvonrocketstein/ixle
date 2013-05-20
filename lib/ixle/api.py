""" ixle.api
"""
import unipath
from report import report
from ixle import util, query
from ixle.schema import Item
from ixle.util import database, conf

def call_agent(agent_nick, item):
    from ixle.agents import registry
    kls = registry[agent_nick]
    agent = kls(path=item.id, settings=conf())
    result = agent.callback(item=item)
    report('called agent, got '+str(result))
    return result

def _space_filename(item):
    i1 = item.fname
    result = call_agent('spacekiller', item)
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
    result = call_agent('typer',item)
    return dict(status='ok')

def moviefinder(path):
    item = path2item(path)
    result = call_agent('moviefinder', item)
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
