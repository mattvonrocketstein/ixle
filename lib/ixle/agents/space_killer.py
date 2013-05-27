"""
"""
import unipath
from report import report
from .base import ItemIterator
from ixle.python import ope

def clean_path_name(pname):
    return pname.replace(' ','_')

class Mover(ItemIterator):
    def move_item(self, item, new_key):
        # TODO: make this a method on databases.
        if self.force:
            old_key = item._id
            item._id = new_key
            self.save(item)
            del self.database[old_key]
            self.record['count_moved'] += 1
        else:
            self.record['count_wouldhave_moved']+=1

class SpaceKiller(Mover): # should be FSIterator
    """ converts spaces to underscores in file names,
        moves the associated documents too.
    """

    nickname = 'spacekiller'

    #@staticmethod
    #def mover_method(src):

    def callback(self, item=None, **kargs):
        report(item.fname)
        src = item.abspath
        new_fname = os.path.split(src)[:-1]#src.item.fname)
        # TODO: be more careful (only replace the last match..)
        dst = src.replace(item.fname, new_fname)
        if src!=dst:
            up = unipath.FSPath(src)
            up.move(dst) # TODO: what does unipath do when dst already exists?
            item.fname = new_fname
            self.move_item(item, dst)
