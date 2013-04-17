""" ixle.views.base
"""

from corkscrew import View as CorkscrewView

class View(CorkscrewView):
    @property
    def db(self):
        return self.settings.database

    @property
    def dupes_db(self):
        return self.settings.dupes_db
