""" ixle.agents.renamer
"""
import unipath as Unipath
from report import report
from ixle.python import ope, opj
from ixle.util import get_heuristics
from ixle.schema import Item
from .base import ItemIterator, DestructionMixin

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

    assert not Unipath.FSPath(dst).exists(), 'file exists'
    assert dst!=item.id,'destination is a noop'
    side_effects.append( MoveFile(item=item, dst=dst) )
    side_effects.append( MoveRecord(old_key=oid, new_key=dst, db=db) )
    return dst, side_effects


class SideEffect(object):
    def __init__(self, **kargs):
        for k,v in kargs.items():
            setattr(self,k,v)
    def __repr__(self):
        return "<SideEffect>"
class DeleteRecord(SideEffect):
    def __repr__(self):
        return "<DeleteRecord: {0} : {1}>".format(self.key)

    def __call__(self):
        self.agent.delete_record(self.key)

class MoveRecord(SideEffect):
    def __repr__(self):
        return "<MoveRecord: {0} : {1}>".format(self.old_key, self.new_key)

    def __call__(self):
        report('moving record', self)
        old_doc = Item.load(self.db, self.old_key)
        new_doc = Item.load(self.db, self.new_key) or Item()
        for attr_name in old_doc._fields:
            setattr(new_doc, attr_name, getattr(old_doc, attr_name))
        new_doc._id = self.new_key
        new_doc.fname = new_doc.unipath.name
        report('saving record', new_doc)
        new_doc.store(self.db)
        return new_doc
        #print 'about to save him'
        #from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        #side_effects.append(lambda: setattr(item,'fname', item.unipath.name))
        #side_effects.append(lambda: setattr(item,'_id', dst))
        #self.new_key

class MoveFile(SideEffect):
    def __repr__(self):
        return "<MoveFile: {0} : {1}>".format(self.item, self.dst)

    def __call__(self):
        self.item.unipath.move(self.dst)

class Renamer(DestructionMixin, ItemIterator):
    nickname = 'renamer'
    requires_path = True

    def handle_does_not_exist(self, item=None):
        err = 'ERROR: file@{0} does not exist.  is the drive mounted?'.format(item.fname)
        report(err)
        self.record['error_count'] += 1
        self.record['last_error'] = err

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
                from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
                if abs_newf in self.database:
                    self.record['error_count'] += 1
                    self.record['last_error'] = absf + ' destination would create duplicate record'
                    return
                else:
                    side_effects.append(
                        DeleteRecord(
                            agent=self, # so there's access to the database
                            key=of))
                    [ x() for x in side_effects ]
                    self.record['moved_count'] += 1
                    self.record['redirect_to'] = item.id
