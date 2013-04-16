""" ixle.views.base
"""

from corkscrew import View as CorkscrewView

class View(CorkscrewView):
    @property
    def db(self):
        return self.settings.database
