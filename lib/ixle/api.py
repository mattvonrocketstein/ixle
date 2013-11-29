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
from ixle.python import isdir
from ixle import util
from ixle.util import database, conf, field_name_to_agent


def fill(field_name, path=None):
    fill_all = path is None
    agent = field_name_to_agent(field_name)
    agent_obj = agent(
        path=path, settings=conf(), fill=fill_all,
        wrap_kbi=False #ugh hack
        )
    result = dict(used_agent=agent.__name__,
                  status='ok')
    result.update(**agent_obj())
    return result

def build_agent_method(name):
    def fxn(path):
        try:
            item = Item.objects.get(path=path)
        except Item.DoesNotExist:
            if isdir(path):
                agent,result = util.call_agent_on_dir(name, path)
            else:
                report("error grabbing item with path="+str(path))
                raise
        else:
            agent, result = util.call_agent_on_item(name, item)
        if not result: result = agent.record
        return dict(result)
    fxn.__name__ = name
    return fxn

def indexer(path):
    from ixle.agents.indexer import Indexer
    agent = Indexer(path=path,settings=conf())
    result = agent()
    return result or dict(status='ok')

elaborate = build_agent_method('elaborate')
stale = build_agent_method('stale')
itagger = build_agent_method('itagger')
imdb = build_agent_method('imdb')
md5 = build_agent_method('md5')
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
    item = Item.objects.get(path=path)
    agent, result = util.call_agent_on_item('typer', item)
    return dict(status='ok')


def moviefinder(path):
    item = Item.objects.get(path=path)
    agent, result = util.call_agent_on_item('moviefinder', item)
    return dict(status='ok')

def kill_directory(directory):
    print 'this is killd'
    path = unipath.path.Path(directory)
    assert path.exists(),(
        'to kill it, the path needs to exist.  '
        'if you just want these items out of the database, '
        'use the unindexer')
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
