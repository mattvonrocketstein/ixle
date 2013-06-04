"""
"""
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
