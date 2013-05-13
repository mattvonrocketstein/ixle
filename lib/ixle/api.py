"""
"""
import unipath
from ixle import util, query

def kill_directory(d):
    from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
    return
    for item in query.key_startswith(
        util.database(), d):
        print item
    path = unpath.path.Path(d)
    print path
