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
from ixle import util
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

def build_agent_method(name):
    def fxn(path):
        try:
            item = Item.objects.get(path=path)
        except Item.DoesNotExist:
            report("error grabbing item with path="+str(path))
            raise
        agent, result = call_agent(name, item)
        if not result: result = agent.record
        return dict(result)
    fxn.__name__ = name
    return fxn

stale = build_agent_method('stale')
itagger = build_agent_method('itagger')
imdb = build_agent_method('imdb')
moviefinder = build_agent_method('moviefinder')
mtagger = build_agent_method('mtagger')
sizer = build_agent_method('sizer')
filer = build_agent_method('filer')
renamer = build_agent_method('renamer')
mimer = build_agent_method('mimer')
slayer = build_agent_method('slayer')
janitor = build_agent_method('janitor')

def unindex(path):
    from ixle.agents.unindex import Unindex
    agent = Unindex(path=path, settings=conf(), force=True)
    result = agent()
    return result or agent.record

def typer(path):
    item = path2item(path)
    agent, result = call_agent('typer', item)
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

def blacklist(path):
    """ kill files like "torrent_downloaded_from_demonoid.txt"
        with a click, and keep the filename in a list.  later,
        any files indexed with that name will be killed automatically,
        but an event will be recorded.
    """
    item = path2item(path)
    fname = item.fname
    from ixle.schema import DSetting
    from ixle.dsettings import FnameBlackList
    from ixle.agents.janitor import Janitor
    z2 = FnameBlackList.get_or_create()
    blacklist = z2.decode()
    assert blacklist is not None
    if fname not in blacklist:
        blacklist.append(fname)
        z2.encode(blacklist)
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    return janitor(path)
