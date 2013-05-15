""" ixle.api
"""
import unipath
from ixle import util, query
from ixle.schema import Item

def _space_filename(item):
    from ixle.agents import registry
    agent_nick = 'spacekiller'
    i1 = item.fname
    kls = registry[agent_nick]
    result = kls(path=item.id).callback(item=item)
    i2 = item.fname
    return dict(
        changed_filename='"{0}" to "{1}"'.format(i1,i2))

def spacekiller(path):
    from ixle.util import database
    db = database()
    item = Item.load(db,path)
    return _space_filename(item)

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
