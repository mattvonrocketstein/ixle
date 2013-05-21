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
    provides = 'fname fext _id'.split()
    nickname = 'index'

    @wrap_kbi
    def __call__(self):
        self.index()

    def callback(self, id=None, **kargs):
        if self.is_ignored(id):
            #report('ignoring')
            return
        assert id is not None, 'this callback takes an id'
        abs_path = id
        rel_name = abs_path.split(sep)[-1]
        extension = splitext(rel_name)
        item = Item(fname=rel_name.decode('utf-8'),
                    fext=extension,
                    _id=abs_path.decode('utf-8'))
        success = self.save(item, quiet=True)
        if not success and self.force:
            report('force-saving.. might be nasty')
            del self.database[item.id]
            report("overwriting data: " + item.fname)
            self.save(item)
        elif success:
            report("fresh data: " + item.fname)

    def index(self):
        report('running index for ' + self.path)
        print
        count = 0
        stuff = list(os.walk(self.path))
        num_files = len(stuff)
        pbar = self.get_progressbar(num_files)
#ProgressBar(widgets=PBAR_WIDGETS, maxval=num_files).start()
        for i in range(num_files):
            root, _dir, files = stuff[i]
            pbar.update(i)
            for rel_name in files:
                count += 1
                self.callback(id=opj(root, rel_name))
        pbar.finish()
        report.console.draw_line()
        report('total files: ' + str(count))
