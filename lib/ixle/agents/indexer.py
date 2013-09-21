""" ixle.agents.indexer
"""

import os

from report import report

from ixle.python import sep, opj, splitext
from ixle.schema import Item
from .base import IxleAgent, wrap_kbi

class Indexer(IxleAgent):
    """ only gets new content, and
        refuses to touch anything already
        mentioned in db
    """
    requires_path = True
    provides = 'fname fext path'.split()
    nickname = 'index'

    @wrap_kbi
    def __call__(self):
        self.index()

    def callback(self, id=None, **kargs):
        if self.is_ignored(id):
            return
        assert id is not None, 'this callback takes an id'
        abs_path = id
        rel_name = abs_path.split(sep)[-1]
        extension = splitext(rel_name)
        data = dict(fext=extension,path=abs_path)
        # abs_path.decode('utf-8'))
        try:
            item = Item.objects.get(path=data['path'])
        except Item.DoesNotExist:
            item = Item(**data)
            item.save()
            report("fresh data: " + item.fname)
        else:
            err = 'item already exists and "force" was not specified'
            assert self.force, err
            #report("overwriting data: " + item.fname)
            self.record['overwrote'] += 1
            item.delete()
            item = Item(**data)
        result = self.save(item)
        return result

    def index(self):
        report('running index for ' + self.path)
        count = 0
        stuff = list(os.walk(self.path))
        num_files = len(stuff)
        pbar = self.get_progressbar(num_files)
        #ProgressBar(widgets=PBAR_WIDGETS, maxval=num_files).start()
        for i in range(num_files):
            root, _dir, files = stuff[i]
            pbar.update(i)
            for rel_name in files:
                fname = opj(root, rel_name)
                count += 1
                self.callback(id=fname)
        pbar.finish()
        report.console.draw_line()
        report('total files: ' + str(count))
