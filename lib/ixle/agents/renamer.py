""" ixle.agents.renamer
"""
import unipath as Unipath
from report import report
from ixle.python import ope, opj
from ixle.util import get_heuristics
from ixle.schema import Item
from .base import ItemIterator, DestructionMixin
from ixle.side_effects import *
from ixle.exceptions import *
def move(item, dst, db):
    report('called for {0} :: {1}'.format(item.fname, dst))
    assert item and dst, 'need a database and fs-dst to execute move'
    assert item.id, 'must be saved to move'
    assert item.exists(), 'must be mounted to move'
    oid = item.id
    odst = dst
    side_effects = []
    if not Unipath.FSPath(dst).isabsolute():
        # item('/foo/bar.txt').move('bar.dst') -->
        #   item('/foo/bar.txt').move('/foo/bar.dst')
        return move(
            item,
            opj(item.unipath.parent, dst), db)

    if Unipath.FSPath(dst).isdir():
        return move(
            item, opj(dst, item.fname), db)

    if Unipath.FSPath(dst).exists():
        raise FileExists(dst)
    assert dst!=item.id,'destination is a noop'
    side_effects.append( MoveFile(item=item, dst=dst) )
    side_effects.append( MoveRecord(old_key=oid, new_key=dst, db=db) )
    item._moved_to = dst
    return dst, side_effects



class Renamer(DestructionMixin, ItemIterator):
    nickname = 'renamer'
    requires_path = True

    def handle_does_not_exist(self, item=None):
        err = 'ERROR: file@{0} does not exist.  is the drive mounted?'.format(item.fname)
        self.report_error(err)

    def callback(self, item, fname=None, **kargs):
        if not item.exists():
            return self.handle_does_not_exist(item=item)
        else:
            more_clean = get_heuristics()['more_clean']
            new_name = more_clean(item)
            report('new name will be: ',new_name)
            if new_name == item.fname:
                self.record['count_skipped'] += 1
                report('name does not differ from suggestion.')
                return
            else:
                of = item.id
                abs_newf, side_effects = move(item, new_name, self.database)
                if abs_newf in self.database:
                    self.report_error(absf + ' destination would create duplicate record')
                    return
                else:
                    side_effects.append(
                        DeleteRecord(
                            agent=self, # so there's access to the database
                            key=of))
                    [ x() for x in side_effects ]
                    self.record['moved_count'] += 1
                    self.record['redirect_to'] = item._moved_to # hack
